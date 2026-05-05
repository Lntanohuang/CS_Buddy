from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from app.db.collections import learning_paths


DEFAULT_PATH_NODES = [
    {
        "node_id": "node_array",
        "title": "数组与顺序表",
        "knowledge_point": "array",
        "order": 1,
        "status": "COMPLETED",
        "difficulty": "BEGINNER",
        "est_minutes": 45,
        "prerequisites": [],
        "is_supplement": False,
    },
    {
        "node_id": "node_sorting",
        "title": "排序算法基础",
        "knowledge_point": "sorting",
        "order": 2,
        "status": "IN_PROGRESS",
        "difficulty": "INTERMEDIATE",
        "est_minutes": 60,
        "prerequisites": ["node_array"],
        "is_supplement": False,
    },
    {
        "node_id": "node_tree",
        "title": "树与二叉树",
        "knowledge_point": "binary_tree",
        "order": 3,
        "status": "PENDING",
        "difficulty": "INTERMEDIATE",
        "est_minutes": 75,
        "prerequisites": ["node_sorting"],
        "is_supplement": False,
    },
]


def build_default_path(user_id: str, subject: str = "数据结构", goal: str = "考试与面试冲刺") -> dict:
    now = datetime.now(timezone.utc)
    nodes = deepcopy(DEFAULT_PATH_NODES)
    return {
        "path_id": f"path_{uuid4().hex}",
        "user_id": user_id,
        "subject": subject,
        "goal": goal,
        "total_nodes": len(nodes),
        "completed_nodes": sum(1 for node in nodes if node["status"] == "COMPLETED"),
        "status": "ACTIVE",
        "est_total_hours": round(sum(node["est_minutes"] for node in nodes) / 60, 1),
        "nodes": nodes,
        "created_at": now,
        "updated_at": now,
    }


def _public_path_doc(document: dict | None) -> dict | None:
    if document is None:
        return None
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


async def create_learning_path(user_id: str, subject: str = "数据结构", goal: str = "考试与面试冲刺") -> dict:
    document = build_default_path(user_id=user_id, subject=subject, goal=goal)
    await learning_paths().insert_one(document)
    return _public_path_doc(document) or document


async def get_active_path(user_id: str) -> dict | None:
    document = await learning_paths().find_one(
        {"user_id": user_id, "status": "ACTIVE"},
        sort=[("updated_at", -1)],
    )
    return _public_path_doc(document)


async def get_or_create_active_path(
    user_id: str,
    subject: str = "数据结构",
    goal: str = "考试与面试冲刺",
) -> dict:
    existing = await get_active_path(user_id)
    if existing is not None:
        return existing
    return await create_learning_path(user_id=user_id, subject=subject, goal=goal)


async def adjust_active_path(user_id: str, knowledge_point: str, action: str) -> dict:
    path = await get_or_create_active_path(user_id=user_id)
    adjusted = adjust_path_after_eval(path, knowledge_point=knowledge_point, action=action)
    await learning_paths().update_one({"path_id": adjusted["path_id"]}, {"$set": adjusted})
    return adjusted


def adjust_path_after_eval(path: dict, knowledge_point: str, action: str) -> dict:
    updated = deepcopy(path)
    nodes = updated.get("nodes", [])

    if action == "ADVANCE":
        for node in nodes:
            if node.get("knowledge_point") == knowledge_point and node.get("status") == "IN_PROGRESS":
                node["status"] = "COMPLETED"
                node["completed_at"] = datetime.now(timezone.utc)
                break
        for node in nodes:
            if node.get("status") == "PENDING":
                node["status"] = "IN_PROGRESS"
                break
    elif action == "SUPPLEMENT":
        base_node = next((node for node in nodes if node.get("knowledge_point") == knowledge_point), None)
        has_existing_supplement = any(
            node.get("knowledge_point") == knowledge_point and node.get("is_supplement")
            for node in nodes
        )
        if base_node and not has_existing_supplement:
            nodes.append({
                "node_id": f"node_sup_{uuid4().hex}",
                "title": f"{knowledge_point} 补充练习",
                "knowledge_point": knowledge_point,
                "order": float(base_node.get("order", len(nodes))) + 0.5,
                "status": "PENDING",
                "difficulty": base_node.get("difficulty", "INTERMEDIATE"),
                "est_minutes": 45,
                "prerequisites": [base_node.get("node_id")],
                "is_supplement": True,
            })

    updated["nodes"] = sorted(nodes, key=lambda node: float(node.get("order", 0)))
    updated["total_nodes"] = len(updated["nodes"])
    updated["completed_nodes"] = sum(1 for node in updated["nodes"] if node.get("status") == "COMPLETED")
    updated["updated_at"] = datetime.now(timezone.utc)
    return updated
