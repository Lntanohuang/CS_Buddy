from __future__ import annotations

from typing import Any


def _route(
    *,
    intent: str,
    active_skill: str,
    resource_type: str | None,
    confidence: float,
    reason: str,
) -> dict[str, Any]:
    return {
        "router": "deterministic_v1",
        "selected_node": "tutor",
        "selected_skill": active_skill,
        "intent": intent,
        "active_skill": active_skill,
        "resource_type": resource_type,
        "confidence": confidence,
        "reason": reason,
    }


def classify_intent(message: str) -> dict[str, Any]:
    """Route a user message to the first production agent slice.

    This deterministic classifier is intentionally small: it gives the graph a
    stable Orchestrator contract before replacing the rules with an LLM router.
    """
    text = message.strip()
    lower = text.lower()

    if "出题" in text or "练习" in text or "quiz" in lower:
        return _route(
            intent="quiz_request",
            active_skill="quiz",
            resource_type="quiz",
            confidence=0.9,
            reason="matched quiz keywords",
        )

    if any(kw in text for kw in ["画图", "图解", "思维导图", "mermaid", "流程图"]):
        return _route(
            intent="visual_explain_request",
            active_skill="explain",
            resource_type="mermaid",
            confidence=0.75,
            reason="matched visual explanation keywords",
        )

    if any(kw in text for kw in ["代码", "示例", "实现", "实操", "debug"]):
        return _route(
            intent="code_help_request",
            active_skill="explain",
            resource_type="code",
            confidence=0.75,
            reason="matched code help keywords",
        )

    if any(kw in text for kw in ["路径", "计划", "路线", "怎么学", "学习安排"]):
        return _route(
            intent="path_planning_request",
            active_skill="clarify",
            resource_type="path",
            confidence=0.7,
            reason="matched path planning keywords",
        )

    if any(kw in text for kw in ["讲讲", "解释", "什么是", "原理", "怎么", "如何", "区别"]) or any(
        kw in lower for kw in ["explain", "how", "what is"]
    ):
        return _route(
            intent="explain_request",
            active_skill="explain",
            resource_type="doc",
            confidence=0.85,
            reason="matched explanation keywords",
        )

    return _route(
        intent="clarify_request",
        active_skill="clarify",
        resource_type=None,
        confidence=0.6,
        reason="fallback to clarification",
    )
