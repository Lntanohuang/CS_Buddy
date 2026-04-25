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


def retrieve(query: str, top_k: int = 3, score_threshold: float = 0.72) -> list[dict]:
    vector_store = _get_vector_store()
    pairs = vector_store.similarity_search_with_relevance_scores(query, k=top_k)

    results: list[dict] = []
    for doc, score in pairs:
        if score < score_threshold:
            continue
        results.append(
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "course": doc.metadata.get("course", ""),
                "score": float(score),
            }
        )
    return results
