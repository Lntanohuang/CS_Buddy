from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    user_profile: dict | None
    active_skill: str | None
    intent: str | None
    resource_type: str | None
    intent_confidence: float | None
    intent_reason: str | None
    orchestrator_trace: dict | None
    memory_context: str | None
