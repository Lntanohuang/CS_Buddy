from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

# 本地中文 Embedding 模型（讯飞 API 不支持 embedding endpoint）
_MODEL_NAME = "shibing624/text2vec-base-chinese"


def get_embeddings() -> Embeddings:
    return HuggingFaceEmbeddings(model_name=_MODEL_NAME)
