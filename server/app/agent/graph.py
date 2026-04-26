from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.skills import SKILLS
from app.agent.state import AgentState
from app.agent.tools import get_profile, search_knowledge
from app.config import settings

TOOLS = [get_profile, search_knowledge]


def _create_model() -> ChatOpenAI:
    model_kwargs = {
        "model": settings.OPENAI_MODEL,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": 0.2,
        "streaming": True,
    }
    if settings.OPENAI_BASE_URL:
        model_kwargs["base_url"] = settings.OPENAI_BASE_URL
    return ChatOpenAI(**model_kwargs)


def tutor_node(state: AgentState) -> dict:
    active_skill = state.get("active_skill") or "explain"
    system_prompt = SKILLS.get(active_skill, SKILLS["explain"])

    model = _create_model().bind_tools(TOOLS)
    model_input = [SystemMessage(content=system_prompt), *state.get("messages", [])]
    response = model.invoke(model_input)

    return {
        "messages": [response],
        "active_skill": active_skill,
    }


def _route_after_tutor(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return END


def build_graph():
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("tutor", tutor_node)
    graph_builder.add_node("tools", ToolNode(TOOLS))

    graph_builder.set_entry_point("tutor")
    graph_builder.add_conditional_edges(
        "tutor",
        _route_after_tutor,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph_builder.add_edge("tools", "tutor")

    checkpointer = MemorySaver()
    return graph_builder.compile(checkpointer=checkpointer)
