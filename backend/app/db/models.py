# models.py

# SQLAlchemy models (documents, metadata)

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .database import Base

class WBResearchDocument(Base):
    __tablename__ = "wb_research_documents"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String, nullable=True)
    markdown_content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("wb_research_documents.id"))
    document = relationship("WBResearchDocument", back_populates="chunks")

    chunk_index = Column(Integer)       # order of the chunk
    chunk_text = Column(Text)           # actual chunk content
    embedding = Column(Vector(384))   # vector embedding (pgvector)