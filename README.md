# PROJECT IDEA

https://www.ctnet.co.uk/my-journey-to-an-ai-powered-research-assistant-in-obsidian-pt1/

https://www.youtube.com/watch?v=j1QcPSLj7u0

https://www.youtube.com/watch?v=TY_LiTrad3c

https://www.youtube.com/watch?v=FDBnyJu_Ndg

https://www.youtube.com/watch?v=DvURiNIvhxA

First docker-compose up:
PostgreSQL container initializes.
wbresearch_db is created automatically (because of POSTGRES_DB).
pgvector is preinstalled (from the image).
FastAPI connects to db:5432 using credentials from .env.
Later docker-compose up / docker-compose restart:
Database persists thanks to the pg_data volume.
You don’t lose your data, and tables stay intact.
To rebuild FastAPI container after code changes:
docker-compose up --build

docker system df
docker container prune -f
docker image prune -f
docker builder prune -f

- Crawl4AI ingestion
- LLM report generation
- Markdown storage
- Vector search (RAG)

                ┌────────────────────┐
                │      Frontend      │
                │  (Web / Desktop)   │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │    API Gateway     │
                └─────────┬──────────┘
          ┌───────────────┼────────────────┐
          │               │                │
┌─────────▼────────┐ ┌────▼─────────┐ ┌────▼──────────┐
│  Ingestion Svc   │ │  RAG Service │ │  Auth Service │
│ (Crawl + Report) │ │  (Chatbot)   │ │ (Optional)    │
└─────────┬────────┘ └────┬─────────┘ └───────────────┘
          │               │
          │               │
 ┌────────▼────────┐ ┌────▼──────────┐
 │ PostgreSQL      │ │ Vector DB     │
 │ (Markdown +     │ │ (Embeddings)  │
 │ Metadata)       │ │ PGVector etc  │
 └─────────────────┘ └───────────────┘

User double-clicks ResearchEngine.exe
            ↓
Launcher starts FastAPI backend (localhost)
            ↓
Opens browser automatically
            ↓
Frontend (local web UI)
            ↓
Backend API
            ↓
Database (local)
            ↓
Vector Store (local)

# Architecture
ResearchEngine/
│
├── launcher.py                 # EXE entrypoint, starts everything automatically
├── backend/
│   ├── docker-entrypoint.sh        
│   ├── Dockerfile
│   ├── requirements.txt            # for docker
│   └── app
│       ├── main.py                 # FastAPI app
│       ├── ingest/
│       │   ├── services
│       │   │   ├── crawler.py      # Crawl4AI integration
│       │   │   ├── chunker.py      # Split markdown into chunks
│       │   │   └── embedder.py     # Create embeddings for RAG
│       │   ├── pipeline.py         # chain services
│       │   ├── repositories.py     # insert md and embeddings to postgreSQL
│       │   └── schemas.py
│       ├── rag/
│       │   ├── retriever.py        # Vector search
│       │   └── chat.py             # RAG chat logic
│       ├── db/
│       │   ├── database.py         # SQLite connection, async
│       │   └── models.py           # SQLAlchemy models (documents, metadata)
│       ├── config/
│       │   └── config.py           # backend settings and parameters
│       ├── utils/
│       │   └── logger.py
│       ├── schemas/
│       │   └── ingest.py
│       └── routes/
│           ├── health.py
│           └── injest.py
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

# Setup
py -3.12 -m venv wbrh_b_venv
powershell: wbrh_b_venv\Scripts\Activate.ps1
pip install fastapi uvicorn sqlalchemy aiosqlite chromadb requests openai pyinstaller aiohttp crawl4ai sentence_transformers

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

document_chunks
-------------+-------------+-----------+----------+---------------------------------------------
   Column    |    Type     | Collation | Nullable |                   Default
-------------+-------------+-----------+----------+---------------------------------------------
 id          | integer     |           | not null | nextval('document_chunks_id_seq'::regclass)
 document_id | integer     |           |          |
 chunk_index | integer     |           |          |
 chunk_text  | text        |           |          |
 embedding   | vector(384) |           |          |
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