from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage, message_chunk_to_message
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
from app.agent.model import create_chat_model
from app.config import settings

TOOLS = [get_profile, search_knowledge]


def _create_model():
    return create_chat_model(temperature=0.2)


async def tutor_node(state: AgentState) -> dict:
    active_skill = state.get("active_skill") or "explain"
    system_prompt = SKILLS.get(active_skill, SKILLS["explain"])

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

    # Replace in-memory checkpoints with MongoDB persistence via settings.MONGO_URI.
    # settings.MONGO_URI defaults to mongodb://localhost:27017.
    mongo_client = MongoClient(settings.MONGO_URI)
    # Use app-level Mongo database name for checkpoint/session state storage.
    checkpointer = AsyncMongoDBSaver(client=mongo_client, db_name=settings.MONGO_DB)
    # compile() usage stays the same; async compatibility is handled by saver methods.
    return graph_builder.compile(checkpointer=checkpointer)
