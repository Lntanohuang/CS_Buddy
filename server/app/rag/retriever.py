from pathlib import Path

from langchain_community.vectorstores import FAISS

from app.rag.store import get_or_build_index

_VECTOR_STORE: FAISS | None = None


def _get_vector_store() -> FAISS:
    global _VECTOR_STORE

    if _VECTOR_STORE is None:
        kb_dir = Path(__file__).resolve().parents[3] / "computerResources"
        index_dir = Path(__file__).resolve().parents[2] / "knowledge_index"
        _VECTOR_STORE = get_or_build_index(kb_dir, index_dir)
    return _VECTOR_STORE


def retrieve(query: str, top_k: int = 3, max_l2_distance: float = 250.0) -> list[dict]:
    """检索知识库。

    FAISS 返回 L2 距离（越小越相似）。
    max_l2_distance: 过滤阈值，超过此距离的结果不返回。
    """
    vector_store = _get_vector_store()
    pairs = vector_store.similarity_search_with_score(query, k=top_k)

    results: list[dict] = []
    for doc, distance in pairs:
        if distance > max_l2_distance:
            continue
        results.append(
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "course": doc.metadata.get("course", ""),
                "header_1": doc.metadata.get("header_1", ""),
                "header_2": doc.metadata.get("header_2", ""),
                "header_3": doc.metadata.get("header_3", ""),
                "score": float(distance),
            }
        )
    return results
