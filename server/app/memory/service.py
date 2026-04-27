"""三层记忆服务：短期（checkpointer）、中期（摘要）、长期（Profile + 事件）。"""

from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.db.collections import session_summaries


# ---------------------------------------------------------------------------
# LLM 工厂（复用 graph.py 的配置）
# ---------------------------------------------------------------------------

def _create_model() -> ChatOpenAI:
    kwargs: dict = {
        "model": settings.OPENAI_MODEL,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": 0.3,
    }
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
    return ChatOpenAI(**kwargs)


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


def _format_messages(messages: list[BaseMessage], limit: int = 20) -> str:
    """格式化消息列表为文本。"""
    lines: list[str] = []
    for msg in messages[-limit:]:
        role = "学生" if isinstance(msg, HumanMessage) else "AI"
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        lines.append(f"{role}: {content[:200]}")
    return "\n".join(lines)


async def load_session_summary(session_id: str) -> str | None:
    """从 MongoDB 加载会话摘要。"""
    doc = await session_summaries().find_one({"session_id": session_id})
    if doc:
        return doc.get("summary_text")
    return None


async def generate_and_store_summary(
    session_id: str,
    messages: list[BaseMessage],
) -> None:
    """用 LLM 生成增量摘要并存入 MongoDB。"""
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
    except Exception as e:
        print(f"[memory] 摘要生成失败: {e}")


def should_trigger_summary(message_count: int, interval: int = 10) -> bool:
    """判断是否应触发摘要提取。"""
    return message_count > 0 and message_count % interval == 0


async def build_memory_context(
    session_id: str,
    message_count: int,
) -> str:
    """构建注入到 system prompt 的记忆上下文。

    Phase B: 当消息数 > 5 时注入会话摘要。
    Phase C: 将扩展为包含 Profile + 事件记忆。
    """
    parts: list[str] = []

    # 中期记忆：会话摘要
    if message_count > 5:
        summary = await load_session_summary(session_id)
        if summary:
            parts.append(f"## 历史对话摘要\n{summary}")

    return "\n\n".join(parts)
