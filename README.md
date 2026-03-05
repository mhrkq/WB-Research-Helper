# PROJECT IDEA

I wanted to create a tool that helps me save and store information from websites (e.g. wikipages, fandom pages, etc) for worldbuilding research.
To keep track of my research, I wanted to be able to ask the tool if certain topics have been researched before.
I also wanted to be able to ask the tool of the topics that I have researched before, because I know I will forget them.

# Flow
User double-clicks ResearchEngine.exe (TBD)
        ↓
Launcher starts FastAPI backend (docker)
        ↓
Opens browser automatically
        ↓
Frontend (local web UI)
        ↓
Backend API
        ↓
Database (docker)
        ↓
Vector Store (docker)

# Architecture
```
WBResearchHelper/
│
├── launcher.py                         # EXE entrypoint, starts everything automatically
├── backend/
│   ├── docker-entrypoint.sh        
│   ├── Dockerfile
│   ├── requirements.txt                # for docker
│   └── app
│       ├── main.py                     # FastAPI app
│       ├── ingest/
│       │   ├── services
│       │   │   ├── crawler.py          # Crawl4AI integration
│       │   │   ├── chunker.py          # Split markdown into chunks
│       │   │   └── embedder.py         # Create embeddings for RAG
│       │   ├── ingest_ pipeline.py     # chain services
│       │   ├── ingest_repositories.py  # insert md and embeddings to postgreSQL
│       │   └── schemas.py
│       ├── llm/
│       │   └── chat_service.py         # RAG chat logic
│       ├── db/
│       │   ├── database.py             # SQLite connection, async
│       │   └── models.py               # SQLAlchemy models (documents, metadata)
│       ├── config/
│       │   └── config.py               # backend settings and parameters
│       ├── utils/
│       │   └── logger.py
│       ├── schemas/
│       │   └── ingest.py
│       └── routes/
│           ├── documents.py
│           ├── health.py
│           ├── ingest.py
│           └── querychat.py
│
├── frontend/
│   ├── index.html                  # dashboard / URL submission
│   ├── chat.html                   # chat interface
│   ├── js/
│   │   └── main.js                 # Handle API calls, DOM updates
│   └── css/
│       └── styles.css
│
├── database/
│   └── wvresearch.db               # PostgreSQL DB
├── db-init/
│   └── 01-init.sql                 # add vector extension to DB before creating tables          
│
├── docker-compose.yml              # easier to run pgvector in docker container than manually installing
├── requirements.txt
└── README.md
```

# Setup
in backend:
py -3.12 -m venv wbrh_b_venv
powershell: wbrh_b_venv\Scripts\Activate.ps1
pip install -r requirements.txt

First docker-compose up:
PostgreSQL container initializes.
wbresearch_db is created automatically (because of POSTGRES_DB).
pgvector is preinstalled (from the image).
FastAPI connects to db:5432 using credentials from .env.
Later docker-compose up / docker-compose restart:
Database persists thanks to the pg_data volume.
Data is not lost, tables stay intact.
To rebuild FastAPI container after code changes:
```
docker-compose up --build
```

```
docker system df
docker compose down
docker volume prune -a
docker image prune -a
docker builder prune -a
```

## Ingestion Pipeline
1. crawl URL, output md
2. store md in db
3. chunk md
4. embed chunks
5. store embeddings in db

### 1. Crawl Content
- [Crawl4AI](https://docs.crawl4ai.com/)
extract:
- metadata
- markdown content

### 3. Store in Database
store in PostgreSQL

wb_research_documents
```
------------------+-----------------------------+-----------+----------+---------------------------------------------------
      Column      |            Type             | Collation | Nullable |                      Default
------------------+-----------------------------+-----------+----------+---------------------------------------------------
 id               | integer                     |           | not null | nextval('wb_research_documents_id_seq'::regclass)
 url              | character varying           |           |          |
 title            | character varying           |           |          |
 markdown_content | text                        |           |          |
 created_at       | timestamp without time zone |           |          | now()
Indexes:
    "wb_research_documents_pkey" PRIMARY KEY, btree (id)
    "wb_research_documents_url_key" UNIQUE CONSTRAINT, btree (url)
Referenced by:
    TABLE "document_chunks" CONSTRAINT "document_chunks_document_id_fkey" FOREIGN KEY (document_id) REFERENCES wb_research_documents(id)
```

document_chunks
```
-------------+-------------+-----------+----------+---------------------------------------------
   Column    |    Type     | Collation | Nullable |                   Default
-------------+-------------+-----------+----------+---------------------------------------------
 id          | integer     |           | not null | nextval('document_chunks_id_seq'::regclass)
 document_id | integer     |           |          |
 chunk_index | integer     |           |          |
 chunk_text  | text        |           |          |
 embedding   | vector(384) |           |          |
```
Indexes:
    "document_chunks_pkey" PRIMARY KEY, btree (id)
    "document_chunks_embedding_idx" hnsw (embedding vector_cosine_ops)
Foreign-key constraints:
    "document_chunks_document_id_fkey" FOREIGN KEY (document_id) REFERENCES wb_research_documents(id)

HNSW indexing (if sufficiently large number of rows)

### 4. Chunk + Embed
chunk markdown:
- split by sentences + character length limits *(switch to word-level?)*
- overlap by characters

### 5. Embed
[Sentence Transformers](https://huggingface.co/sentence-transformers)
model: all-MiniLM-L6-v2
vector size: 384

## Chatbot (RAG Service)
- embed query
- retrieve context
- call LLM
- return answer

### 1. Embed User Query
generate embedding for query

### 2. Vector Search
search in research_chunks table

Retrieve:
- top 5 most relevant chunks
- include document metadata

### 3. RAG Prompt
send to LLM:

System:
You are a research assistant. Use the provided research context.

Context:
<retrieved markdown chunks>

User:
any research on fossil fuels?

### 4. Response Modes
2 modes:

Mode A — Return Full Markdown File
If intent = "show research"
Return stored markdown document directly.

Mode B — Summarize from RAG
If question is analytical:
"How are fossil fuels formed?"
LLM synthesizes answer using retrieved chunks.

# Production Stack
FastAPI
PostgreSQL
PGVector
maybe Redis
```
 Layer       | Technology                 
 ----------- | -------------------------- 
 API         | FastAPI                    
 Async Tasks | Celery / BackgroundTasks   
 Crawl       | Crawl4AI                   
 LLM         | OpenAI / local model       
 DB          | PostgreSQL                 
 Vector      | PGVector                   
 Cache       | Redis                      
 Frontend    | React          
 Storage     | S3 (optional for raw HTML) 
```

# Event-Driven Version (More Scalable)
instead of synchronous ingestion
User submits URL
        ↓
API stores job
        ↓
Message Queue
        ↓
Worker processes crawl + LLM + embeddings
        ↓
Store in DB
        ↓
Notify user

# Questions
- 500 character chunks too small size?
- RAG retrieval top 5 too small size?
- improvements to RAG? 
- document metadata filtering? - optional document filtering by doc id/title
- hybrid search (BM25 + vector)? 

- reranker model?
dense embeddings retrieve semantically similar chunks, but not necessarily the most precise ones
current embedding model (all-MiniLM-L6-v2) encodes query and chunks separately
reranker takes (query, chunk) pairs 
scores how relevant the chunk is to the query
reorders retrieved results
e.g. 
instead of top_k = 5,
top_k = 20 (vector search)
rerank top 20
send top 5 to llm
higher precision and recall

cross-encoder/ms-marco-MiniLM-L-6-v2
Same ecosystem (sentence-transformers)
small & fast (~120MB)
Very easy to integrate
Strong ranking quality
Widely used in production RAG systems
Works great with MiniLM embeddings (same family)

BAAI/bge-reranker-base
Slightly better ranking performance
More modern model
Strong multilingual capabilities

Heavier (~400MB)
Slower
More memory usage
Overkill for most research/document RAG setups

querychat endpoint
    ↓
RetrievalService
    ↓
Vector search (top_k=20)
    ↓
RerankService
    ↓
Top 5 chunks
    ↓
LLMService (Gemini)
    ↓
Response

- conversation memory?
- knowledge graph & structured knowledge queries?
- streaming response (UX)?

- add youtube transcript crawler? crawl4ai
- or [video context engine](https://www.reddit.com/r/LocalLLaMA/comments/1pbhbdy/project_videocontext_engine_a_fully_local/)
- Model Context Protocol (MCP)?

# References

https://www.ctnet.co.uk/my-journey-to-an-ai-powered-research-assistant-in-obsidian-pt1/

https://www.youtube.com/watch?v=j1QcPSLj7u0

https://www.youtube.com/watch?v=TY_LiTrad3c

https://www.youtube.com/watch?v=FDBnyJu_Ndg

https://www.youtube.com/watch?v=DvURiNIvhxA