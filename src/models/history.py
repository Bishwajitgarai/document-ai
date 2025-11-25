"""Database models for chat history and documents."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base


class Document(Base):
    """Model for tracking uploaded documents per user."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer)
    chunks_created = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="documents")


class QueryHistory(Base):
    """Model for storing query/chat history per user."""
    
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON)  # Store source documents as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="query_history")
