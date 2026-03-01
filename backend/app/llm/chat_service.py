# backend/app/llm/chat_service.py

import os
from openai import AsyncOpenAI
from fastapi.concurrency import run_in_threadpool
from google import genai

# client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# async def generate_answer(question: str, context_chunks: list[str]) -> str:
#     """
#     Generates a grounded answer using retrieved chunks.
#     """

#     context_text = "\n\n".join(context_chunks)

#     system_prompt = """
# You are a research assistant.

# Answer ONLY using the provided context.
# If the answer is not in the context, say you don't know.
# Be precise and factual.
# """

#     user_prompt = f"""
# Context:
# {context_text}

# Question:
# {question}
# """

#     response = await client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         temperature=0.2,
#     )

#     return response.choices[0].message.content

def _generate_answer_sync(question: str, context_chunks: list[str]) -> str:
    """
    Synchronous function to generate an answer using Gemini 3.
    """
    context_text = "\n\n".join(context_chunks)

    prompt = f"""
You are a research assistant.

Answer ONLY using the provided context.
If the answer is not in the context, say you don't know.
Be precise and factual.

Context:
{context_text}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


async def generate_answer(question: str, context_chunks: list[str]) -> str:
    """
    Async wrapper for FastAPI endpoints.
    """
    return await run_in_threadpool(_generate_answer_sync, question, context_chunks)