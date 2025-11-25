"""Pydantic schemas for history and documents."""
from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    """Schema for document information."""
    id: int
    document_id: str
    filename: str
    file_size: int | None
    chunks_created: int | None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class QueryHistoryResponse(BaseModel):
    """Schema for query history."""
    id: int
    query: str
    answer: str
    sources: list | None
    created_at: datetime
    
    class Config:
        from_attributes = True
