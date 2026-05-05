from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, message_chunk_to_message
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pymongo import MongoClient

# langgraph-checkpoint-mongodb==0.3.1 exposes MongoDBSaver (async-capable methods)
# but may not export AsyncMongoDBSaver by name in all versions.
try:
    from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
except ImportError:  # pragma: no cover - compatibility fallback
    from langgraph.checkpoint.mongodb import MongoDBSaver as AsyncMongoDBSaver

from app.agent.skills import SKILLS
from app.agent.state import AgentState
from app.agent.tools import get_profile, search_knowledge
from app.agent.intent import classify_intent
from app.agent.model import create_chat_model
from app.config import settings

TOOLS = [get_profile, search_knowledge]


def _create_model():
    return create_chat_model(temperature=0.2)


async def orchestrator_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    latest_user_text = ""
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            content = message.content
            latest_user_text = content if isinstance(content, str) else str(content)
            break

    route = classify_intent(latest_user_text)
    return {
        "active_skill": route["active_skill"],
        "intent": route["intent"],
        "resource_type": route["resource_type"],
        "intent_confidence": route["confidence"],
        "intent_reason": route["reason"],
        "orchestrator_trace": route,
    }


async def _skill_node(state: AgentState, skill: str) -> dict:
    active_skill = state.get("active_skill") or skill
    system_prompt = SKILLS.get(skill, SKILLS["explain"])

    memory_block = state.get("memory_context") or ""
    if memory_block:
        system_prompt = system_prompt + "\n\n" + memory_block

    model = _create_model().bind_tools(TOOLS)
    model_input = [SystemMessage(content=system_prompt), *state.get("messages", [])]

    response_chunk = None
    async for chunk in model.astream(model_input):
        response_chunk = chunk if response_chunk is None else response_chunk + chunk

    response = (
        message_chunk_to_message(response_chunk)
        if response_chunk is not None
        else AIMessage(content="")
    )

    return {
        "messages": [response],
        "active_skill": skill,
    }


async def explain_agent_node(state: AgentState) -> dict:
    return await _skill_node(state, "explain")


async def quiz_agent_node(state: AgentState) -> dict:
    return await _skill_node(state, "quiz")


async def clarify_agent_node(state: AgentState) -> dict:
    return await _skill_node(state, "clarify")


def _route_from_orchestrator(
    state: AgentState,
) -> Literal["explain_agent", "quiz_agent", "clarify_agent"]:
    selected = (state.get("orchestrator_trace") or {}).get("selected_node")
    if selected == "quiz_agent":
        return "quiz_agent"
    if selected == "clarify_agent":
        return "clarify_agent"
    return "explain_agent"


def _route_after_skill(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return END


def _route_after_tools(
    state: AgentState,
) -> Literal["explain_agent", "quiz_agent", "clarify_agent"]:
    active_skill = state.get("active_skill")
    if active_skill == "quiz":
        return "quiz_agent"
    if active_skill == "clarify":
        return "clarify_agent"
    return "explain_agent"


def build_graph():
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("orchestrator", orchestrator_node)
    graph_builder.add_node("explain_agent", explain_agent_node)
    graph_builder.add_node("quiz_agent", quiz_agent_node)
    graph_builder.add_node("clarify_agent", clarify_agent_node)
    graph_builder.add_node("tools", ToolNode(TOOLS))

    graph_builder.set_entry_point("orchestrator")
    graph_builder.add_conditional_edges(
        "orchestrator",
        _route_from_orchestrator,
        {
            "explain_agent": "explain_agent",
            "quiz_agent": "quiz_agent",
            "clarify_agent": "clarify_agent",
        },
    )
    for node_name in ("explain_agent", "quiz_agent", "clarify_agent"):
        graph_builder.add_conditional_edges(
            node_name,
            _route_after_skill,
            {
                "tools": "tools",
                END: END,
            },
        )
    graph_builder.add_conditional_edges(
        "tools",
        _route_after_tools,
        {
            "explain_agent": "explain_agent",
            "quiz_agent": "quiz_agent",
            "clarify_agent": "clarify_agent",
        },
    )

    # Replace in-memory checkpoints with MongoDB persistence via settings.MONGO_URI.
    # settings.MONGO_URI defaults to mongodb://localhost:27017.
    mongo_client = MongoClient(settings.MONGO_URI)
    # Use app-level Mongo database name for checkpoint/session state storage.
    checkpointer = AsyncMongoDBSaver(client=mongo_client, db_name=settings.MONGO_DB)
    # compile() usage stays the same; async compatibility is handled by saver methods.
    return graph_builder.compile(checkpointer=checkpointer)
