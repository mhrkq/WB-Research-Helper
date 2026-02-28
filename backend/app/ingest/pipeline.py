# backend/app/ingest/pipeline.py

# 1. crawl URL, output md
# 2. store md in db
# 3. chunk md
# 4. embed chunks
# 5. store embeddings in db

from .services.crawler import crawl_url
from .services.chunker import create_list_of_chunks
from .services.embedder import embed_chunks
from .repositories import save_md, save_embeddings
from ..db.database import AsyncSessionLocal

async def run_ingestion(url: str):
    async with AsyncSessionLocal() as session:
        md_content, title = await crawl_url(url)
        document_id = await save_md(session, url, md_content, title)
        
        chunks = create_list_of_chunks(url, title, md_content)
        embeddings = embed_chunks(chunks)
        
        chunk_texts = [c["chunk_text"] for c in chunks]
        await save_embeddings(session, document_id, chunk_texts, embeddings)
        
        return {"status": "success", "document_id": document_id, "chunks": len(chunks)}     