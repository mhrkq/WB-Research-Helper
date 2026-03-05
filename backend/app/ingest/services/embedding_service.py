# backend/app/ingest/services/embedder.py

from typing import List, Dict
import numpy as np

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_chunks(chunks: List[Dict]) -> List[List[float]]:
    """
    Accepts a list of chunk dicts (from chunker.py) and returns a list of embeddings.

    Each embedding corresponds to chunk['chunk_text'].
    """
    # extract text to embed
    texts = [chunk["chunk_text"] for chunk in chunks]

    embeddings = model.encode(texts, show_progress_bar=False)

    # convert embeddings to list of floats for storage
    if isinstance(embeddings, np.ndarray):
        embeddings = embeddings.tolist()

    return embeddings