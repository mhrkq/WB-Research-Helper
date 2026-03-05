# backend/app/query/services/query_pipeline.py

# call query_similar_chunks
# convert rows into structured dicts
# call reranker_service
# return final top_k chunks

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .services.embedding_service import embed_query
from .services.retrieval_service import retrieve_chunks
from .services.rerank_service import rerank_documents
from .services.answer_service import generate_rag_answer


async def run_query(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    document_id: Optional[int] = None,
    title_contains: Optional[str] = None,
):

    if not query.strip():
        raise ValueError("Query cannot be empty")

    # 1 Embed query
    query_embedding = embed_query(query)

    # 2 Retrieve candidates
    candidates = await retrieve_chunks(
        session=session,
        query_embedding=query_embedding,
        top_k=top_k * 3,
        document_id=document_id,
        title_contains=title_contains,
    )

    if not candidates:
        raise ValueError("No relevant documents found")

    # 3 Rerank
    reranked = rerank_documents(query, candidates, top_k)

    # 4 Generate answer
    chunk_texts = [doc["content"] for doc in reranked]
    answer = await generate_rag_answer(query, chunk_texts)

    return {
        "answer": answer,
        "results": [
            {
                "document_id": doc["metadata"]["document_id"],
                "chunk_index": doc["metadata"]["chunk_index"],
                "chunk_text": doc["content"],
                "vector_similarity": doc["metadata"]["similarity"],
                "rerank_score": doc["rerank_score"],
            }
            for doc in reranked
        ],
    }