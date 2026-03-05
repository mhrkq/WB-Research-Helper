# backend/app/query/services/answer_service.py

from ...llm.chat_service import generate_answer


async def generate_rag_answer(query, chunk_texts):
    return await generate_answer(query, chunk_texts)