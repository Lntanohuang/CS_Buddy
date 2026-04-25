from pathlib import Path

from langchain_community.vectorstores import FAISS

from app.rag.embeddings import get_embeddings
from app.rag.loader import load_and_split_documents


def build_index(kb_dir: Path, index_dir: Path) -> FAISS:
    documents = load_and_split_documents(kb_dir)
    if not documents:
        raise ValueError(f"No markdown documents found under {kb_dir}")

    vector_store = FAISS.from_documents(documents, get_embeddings())
    index_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(index_dir))
    return vector_store


def load_index(index_dir: Path) -> FAISS | None:
    faiss_file = index_dir / "index.faiss"
    pkl_file = index_dir / "index.pkl"
    if not faiss_file.exists() or not pkl_file.exists():
        return None

    return FAISS.load_local(
        str(index_dir),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


def get_or_build_index(kb_dir: Path, index_dir: Path) -> FAISS:
    index = load_index(index_dir)
    if index is not None:
        return index
    return build_index(kb_dir, index_dir)
