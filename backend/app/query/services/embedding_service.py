# backend/app/query/services/embedding_service.py

from ...ingest.services.embedding_service import embed_chunks


def embed_query(query: str):
    embedding = embed_chunks([{"chunk_text": query}])[0]
    return embedding