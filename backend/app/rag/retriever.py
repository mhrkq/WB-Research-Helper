# Vector search

import asyncio

async def retrieve_relevant_chunks(text: str) -> str:
    """
    Dummy function for testing.
    Normally, this would send 'text' to your LLM and return the markdown output.
    """
    await asyncio.sleep(0.1)  # simulate async LLM call
    return f"# Dummy Report\n\nOriginal text: {text[:200]}..."  # return dummy markdown