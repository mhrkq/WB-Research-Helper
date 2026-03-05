# backend/app/query/services/rerank.py

from sentence_transformers import CrossEncoder

_reranker = None


def get_model():
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    return _reranker


def rerank_documents(query, documents, top_k):

    model = get_model()

    pairs = [(query, doc["content"]) for doc in documents]

    scores = model.predict(pairs)

    for doc, score in zip(documents, scores):
        doc["rerank_score"] = float(score)

    documents.sort(key=lambda x: x["rerank_score"], reverse=True)

    return documents[:top_k]