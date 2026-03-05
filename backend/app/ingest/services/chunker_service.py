# chunker.py

# split markdown into chunks
# overlapping chunks to ensure context continuity for embeddings
# word-level chunking is safer for LLM context than character-level
# change to word-level chunking?
# clean text by removing multiple whitespaces and newlines

from typing import List, Dict
import re

def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[str]:

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            if len(current_chunk.strip()) >= 20:
                chunks.append(current_chunk.strip())

            # overlap logic
            overlap_text = current_chunk[-chunk_overlap:]
            current_chunk = overlap_text + " " + sentence

    if len(current_chunk.strip()) >= 20:
        chunks.append(current_chunk.strip())

    return chunks


def create_list_of_chunks(
    url: str,
    title: str | None,
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict]:
    """
    Converts a full document into a list of chunk dicts with metadata.
    
    Each dict has:
    - chunk_index: the order of the chunk
    - chunk_text: the actual chunk content
    - metadata: url and title
    """
    raw_chunks = split_text_into_chunks(text, chunk_size, chunk_overlap)
    
    return [
        {
            "chunk_index": idx,
            "chunk_text": chunk,
            "metadata": {"url": str(url), "title": title}
        }
        for idx, chunk in enumerate(raw_chunks)
    ]