"""三层记忆服务：短期（checkpointer）、中期（摘要）、长期（Profile + 事件）。"""

from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agent.model import create_chat_model
from app.db.collections import session_summaries, user_profiles


# ---------------------------------------------------------------------------
# LLM 工厂（复用 graph.py 的配置）
# ---------------------------------------------------------------------------

def _create_model():
    return create_chat_model(temperature=0.3)


def _format_messages(messages: list[BaseMessage], limit: int = 20) -> str:
    """格式化消息列表为文本。"""
    lines: list[str] = []
    for msg in messages[-limit:]:
        role = "学生" if isinstance(msg, HumanMessage) else "AI"
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        lines.append(f"{role}: {content[:200]}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Phase B: 中期记忆 — 增量摘要
# ---------------------------------------------------------------------------

SUMMARY_PROMPT = """你是一个对话摘要助手。请根据以下师生对话记录和已有摘要，生成更新后的摘要。

使用 ADD/UPDATE/NOOP 策略：
- ADD: 新出现的知识点、学习进展、用户偏好、关键问答
- UPDATE: 修正或补充已有条目（如掌握度变化）
- NOOP: 信息已包含则不重复

已有摘要：
{existing_summary}

最近对话：
{recent_messages}

请直接输出更新后的完整摘要，包含以下要点（如有）：
- 用户基本信息（姓名、专业、水平等）
- 已讨论的知识点及掌握情况
- 用户的学习目标和偏好
- 待解决的疑问
简洁明了，不超过 300 字。"""


async def load_session_summary(session_id: str) -> str | None:
    doc = await session_summaries().find_one({"session_id": session_id})
    if doc:
        return doc.get("summary_text")
    return None


async def generate_and_store_summary(
    session_id: str,
    messages: list[BaseMessage],
    user_id: str | None = None,
) -> None:
    """用 LLM 生成增量摘要，存入 MongoDB，并触发长期记忆提取。"""
    try:
        existing = await load_session_summary(session_id) or "无"
        recent_text = _format_messages(messages)

        prompt = SUMMARY_PROMPT.format(
            existing_summary=existing,
            recent_messages=recent_text,
        )

        model = _create_model()
        response = await model.ainvoke([HumanMessage(content=prompt)])
        summary_text = response.content if isinstance(response.content, str) else str(response.content)

        await session_summaries().update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "summary_text": summary_text,
                    "updated_at": datetime.now(timezone.utc),
                },
                "$inc": {"extract_count": 1},
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": datetime.now(timezone.utc),
                },
            },
            upsert=True,
        )
        print(f"[memory] 摘要已更新: session={session_id}, len={len(summary_text)}")

        # Phase C: 摘要后触发事件提取 + Profile 更新
        if user_id:
            try:
                await extract_and_store_events(session_id, user_id, summary_text)
            except Exception as e:
                print(f"[memory] 事件提取失败: {e}")
    except Exception as e:
        print(f"[memory] 摘要生成失败: {e}")


def should_trigger_summary(message_count: int, interval: int = 10) -> bool:
    # 触发阈值为 >= interval，比如 message_count=20（10轮对话）时 >= 10 成立
    return message_count >= interval


# ---------------------------------------------------------------------------
# Phase C: 长期记忆 — 结构化 Profile
# ---------------------------------------------------------------------------

DEFAULT_PROFILE = {
    "major": "计算机科学与技术",
    "current_level": "INTERMEDIATE",
    "learning_goal": "EXAM_PREP",
    "preferred_style": "PRACTICE",
    "cognitive_style": "PRACTICAL",
    "error_patterns": [],
    "daily_time_minutes": 60,
    "knowledge_mastery": {},
    "weak_points": [],
}


async def load_user_profile(user_id: str) -> dict | None:
    doc = await user_profiles().find_one({"user_id": user_id})
    if doc:
        doc.pop("_id", None)
        return doc
    return None


async def ensure_default_profile(user_id: str) -> dict:
    existing = await load_user_profile(user_id)
    if existing:
        return existing
    profile = {
        "user_id": user_id,
        **DEFAULT_PROFILE,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    await user_profiles().insert_one(profile)
    profile.pop("_id", None)
    return profile


def _format_profile(profile: dict) -> str:
    """将 Profile dict 格式化为可读文本。"""
    lines = [
        f"- 专业: {profile.get('major', '未知')}",
        f"- 水平: {profile.get('current_level', '未知')}",
        f"- 学习目标: {profile.get('learning_goal', '未知')}",
        f"- 偏好风格: {profile.get('preferred_style', '未知')}",
    ]
    mastery = profile.get("knowledge_mastery", {})
    if mastery:
        items = ", ".join(f"{k}: {v:.0%}" for k, v in mastery.items())
        lines.append(f"- 知识掌握: {items}")
    weak = profile.get("weak_points", [])
    if weak:
        lines.append(f"- 薄弱点: {', '.join(weak)}")
    errors = profile.get("error_patterns", [])
    if errors:
        lines.append(f"- 易错点: {', '.join(errors[:5])}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Phase C: 长期记忆 — 事件提取
# ---------------------------------------------------------------------------

EVENT_EXTRACT_PROMPT = """从以下对话摘要中，提取值得长期记忆的学习事件。

仅提取以下类型：
- 用户反复出错或混淆的概念
- 用户突破性的理解
- 用户明确表达的偏好或需求
- 重要的学习进展

每条事件独占一行，以 "- " 开头。
如果没有值得记忆的事件，只输出"无"。

对话摘要：
{summary}"""


async def extract_and_store_events(
    session_id: str,
    user_id: str,
    summary_text: str,
) -> None:
    """从摘要中提取事件记忆，存入 FAISS + MongoDB。"""
    from app.memory.event_store import add_event, persist_event_to_mongo

    model = _create_model()
    prompt = EVENT_EXTRACT_PROMPT.format(summary=summary_text)
    response = await model.ainvoke([HumanMessage(content=prompt)])
    text = response.content if isinstance(response.content, str) else str(response.content)

    if text.strip() == "无":
        print("[memory] 无新事件")
        return

    events = [line.lstrip("- ").strip() for line in text.strip().split("\n") if line.strip().startswith("- ")]
    for event_text in events:
        if not event_text:
            continue
        add_event(event_text, user_id, session_id)
        await persist_event_to_mongo(event_text, user_id, session_id)
        print(f"[memory] 事件已存储: {event_text[:50]}")


# ---------------------------------------------------------------------------
# 统一入口：构建 memory_context
# ---------------------------------------------------------------------------

async def build_memory_context(
    session_id: str,
    message_count: int,
    user_id: str | None = None,
    query: str | None = None,
) -> str:
    """构建注入到 system prompt 的记忆上下文。

    - Phase B: 会话摘要（消息数 > 5 时注入）
    - Phase C: 用户画像（始终注入）+ 相关事件记忆（语义检索）
    """
    parts: list[str] = []

    # 长期记忆：用户画像
    if user_id:
        profile = await load_user_profile(user_id)
        if profile:
            parts.append(f"## 用户画像\n{_format_profile(profile)}")

    # 中期记忆：会话摘要
    if message_count > 5:
        summary = await load_session_summary(session_id)
        if summary:
            parts.append(f"## 历史对话摘要\n{summary}")

    # 长期记忆：事件记忆检索
    if user_id and query:
        try:
            from app.memory.event_store import search_events
            events = search_events(query, user_id, top_k=3)
            if events:
                event_list = "\n".join(f"- {e}" for e in events)
                parts.append(f"## 相关学习记录\n{event_list}")
        except Exception:
            pass

    return "\n\n".join(parts)
