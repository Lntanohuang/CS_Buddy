from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


_COURSE_MAP = {
    "Computer-operating-system-notes": "操作系统",
    "computer-organization": "计算机组成原理",
}


def _derive_course(file_path: Path) -> str:
    return _COURSE_MAP.get(file_path.parent.name, file_path.parent.name)


def load_and_split_documents(kb_dir: Path) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "header_1"),
            ("##", "header_2"),
            ("###", "header_3"),
        ],
        strip_headers=False,
    )
    chunk_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    documents: list[Document] = []
    for md_file in sorted(kb_dir.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        split_docs = header_splitter.split_text(text)
        if not split_docs:
            split_docs = [Document(page_content=text, metadata={})]

        for split_doc in split_docs:
            metadata = {
                "source": md_file.name,
                "course": _derive_course(md_file),
                "header_1": split_doc.metadata.get("header_1", ""),
                "header_2": split_doc.metadata.get("header_2", ""),
                "header_3": split_doc.metadata.get("header_3", ""),
            }
            doc = Document(page_content=split_doc.page_content, metadata=metadata)
            if len(doc.page_content) <= 800:
                documents.append(doc)
                continue
            documents.extend(chunk_splitter.split_documents([doc]))

    return documents
