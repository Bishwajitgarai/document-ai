"""Pydantic models for request and response validation."""
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response model for file upload."""
    status: str
    filename: str
    document_id: str
    chunks_created: int
    message: str


class QueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., min_length=1, description="The question to ask")
    k: int = Field(default=4, ge=1, le=10, description="Number of documents to retrieve")


class Source(BaseModel):
    """Source document information."""
    content: str
    metadata: dict


class QueryResponse(BaseModel):
    """Response model for RAG query."""
    query: str
    answer: str
    sources: list[Source]
    

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
