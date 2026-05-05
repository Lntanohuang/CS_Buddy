from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from app.models.schemas import EvaluationAnswer
from app.db.collections import evaluations
from app.learning_path.service import adjust_active_path
from app.notifications.service import create_notification


DEFAULT_QUESTIONS = [
    {
        "question_id": "q_sort_1",
        "type": "SINGLE_CHOICE",
        "content": "快速排序平均时间复杂度是多少？",
        "options": [
            {"key": "A", "value": "O(n)"},
            {"key": "B", "value": "O(n log n)"},
            {"key": "C", "value": "O(n^2)"},
        ],
        "correct_answer": "B",
        "explanation": "快速排序平均情况下每层分区总成本为 O(n)，递归深度约为 log n。",
    },
    {
        "question_id": "q_sort_2",
        "type": "FILL_BLANK",
        "content": "快速排序的核心思想通常称为____。",
        "options": [],
        "correct_answer": "分治",
        "explanation": "快速排序通过基准分区，再递归处理左右子问题，属于分治思想。",
    },
    {
        "question_id": "q_sort_3",
        "type": "SINGLE_CHOICE",
        "content": "快速排序最坏时间复杂度是什么？",
        "options": [
            {"key": "A", "value": "O(n log n)"},
            {"key": "B", "value": "O(n^2)"},
            {"key": "C", "value": "O(log n)"},
        ],
        "correct_answer": "B",
        "explanation": "当分区极不均衡时，递归深度退化为 n，整体复杂度为 O(n^2)。",
    },
]


def build_evaluation(user_id: str, eval_type: str, knowledge_point: str) -> dict:
    now = datetime.now(timezone.utc)
    questions = deepcopy(DEFAULT_QUESTIONS)
    return {
        "eval_id": f"eval_{uuid4().hex}",
        "user_id": user_id,
        "type": eval_type,
        "knowledge_point": knowledge_point,
        "score": None,
        "mastery_level": None,
        "learning_efficiency": None,
        "progress_trend": None,
        "weak_point_analysis": [],
        "question_count": len(questions),
        "correct_count": None,
        "time_spent_seconds": None,
        "status": "PENDING",
        "questions": questions,
        "recommendation": None,
        "created_at": now,
        "updated_at": now,
    }


def _public_eval_doc(document: dict | None) -> dict | None:
    if document is None:
        return None
    public_doc = dict(document)
    public_doc.pop("_id", None)
    return public_doc


async def create_evaluation(user_id: str, eval_type: str, knowledge_point: str) -> dict:
    document = build_evaluation(user_id, eval_type, knowledge_point)
    await evaluations().insert_one(document)
    return _public_eval_doc(document) or document


async def get_evaluation(eval_id: str) -> dict | None:
    document = await evaluations().find_one({"eval_id": eval_id})
    return _public_eval_doc(document)


async def list_evaluations(user_id: str, limit: int = 20) -> list[dict]:
    cursor = (
        evaluations()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )
    return [_public_eval_doc(doc) or doc async for doc in cursor]


async def submit_evaluation(
    eval_id: str,
    answers: list[EvaluationAnswer],
    time_spent_seconds: int | None = None,
) -> dict | None:
    evaluation = await get_evaluation(eval_id)
    if evaluation is None:
        return None

    scored = score_evaluation(evaluation, answers, time_spent_seconds)
    recommendation = scored.get("recommendation") or {}
    action = recommendation.get("action")
    if action:
        adjusted_path = await adjust_active_path(
            user_id=scored["user_id"],
            knowledge_point=scored["knowledge_point"],
            action=action,
        )
        scored["path_adjustment"] = {
            "path_id": adjusted_path["path_id"],
            "action": action,
            "completed_nodes": adjusted_path["completed_nodes"],
            "total_nodes": adjusted_path["total_nodes"],
        }
    await _create_eval_notifications(scored)
    await evaluations().update_one({"eval_id": eval_id}, {"$set": scored})
    return scored


async def _create_eval_notifications(evaluation: dict) -> None:
    try:
        score = evaluation.get("score")
        mastery = evaluation.get("mastery_level")
        knowledge_point = evaluation.get("knowledge_point", "本次")
        user_id = evaluation.get("user_id")
        if not user_id:
            return

        mastery_label = f"{round(float(mastery) * 100)}%" if mastery is not None else "-"
        await create_notification(
            user_id=user_id,
            notification_type="EVAL_RESULT",
            title=f"{knowledge_point} 测评已完成",
            content=f"得分 {score} 分，掌握度 {mastery_label}",
            action_url="/app/evaluate",
        )

        recommendation = evaluation.get("recommendation") or {}
        message = recommendation.get("message")
        if message:
            await create_notification(
                user_id=user_id,
                notification_type="STUDY_REMINDER",
                title="学习路径已调整",
                content=str(message),
                action_url="/app/path",
            )
    except Exception:
        return


def score_evaluation(evaluation: dict, answers: list[EvaluationAnswer], time_spent_seconds: int | None = None) -> dict:
    answer_map = {item.question_id: item.answer.strip() for item in answers}
    questions = deepcopy(evaluation.get("questions", []))
    correct_count = 0
    weak_points: list[str] = []

    for index, question in enumerate(questions, start=1):
        user_answer = answer_map.get(question["question_id"], "")
        correct_answer = str(question.get("correct_answer", "")).strip()
        is_correct = user_answer.lower() == correct_answer.lower()
        question["user_answer"] = user_answer
        question["is_correct"] = is_correct
        if is_correct:
            correct_count += 1
        else:
            weak_points.append(f"第{index}题: {question.get('content', '')[:40]}")

    question_count = len(questions)
    mastery = correct_count / question_count if question_count else 0.0
    score = round(mastery * 100)
    duration = time_spent_seconds or 180
    speed_factor = 180 / max(duration, 1)
    learning_efficiency = min(1.0, round(mastery * speed_factor, 2))

    if mastery >= 0.7:
        recommendation = {
            "action": "ADVANCE",
            "message": "掌握良好，建议继续学习下一个知识点。",
            "next_node_id": None,
        }
    elif mastery >= 0.4:
        recommendation = {
            "action": "SUPPLEMENT",
            "message": "部分掌握，建议添加补充练习。",
        }
    else:
        recommendation = {
            "action": "RETREAT",
            "message": "掌握不足，建议回顾前置知识。",
        }

    updated = {
        **evaluation,
        "questions": questions,
        "score": score,
        "mastery_level": round(mastery, 2),
        "learning_efficiency": learning_efficiency,
        "progress_trend": "STABLE",
        "weak_point_analysis": weak_points,
        "correct_count": correct_count,
        "time_spent_seconds": duration,
        "status": "ANALYZED",
        "recommendation": recommendation,
        "updated_at": datetime.now(timezone.utc),
    }
    return updated
