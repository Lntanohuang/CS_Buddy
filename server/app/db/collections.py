from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongo import get_db


def user_profiles() -> AsyncIOMotorCollection:
    return get_db()["user_profiles"]


def session_summaries() -> AsyncIOMotorCollection:
    return get_db()["session_summaries"]


def memory_events() -> AsyncIOMotorCollection:
    return get_db()["memory_events"]


def retrieval_logs() -> AsyncIOMotorCollection:
    return get_db()["retrieval_logs"]


def chat_messages() -> AsyncIOMotorCollection:
    return get_db()["chat_messages"]


def evaluations() -> AsyncIOMotorCollection:
    return get_db()["evaluations"]


def learning_paths() -> AsyncIOMotorCollection:
    return get_db()["learning_paths"]


def resource_feedbacks() -> AsyncIOMotorCollection:
    return get_db()["resource_feedbacks"]
