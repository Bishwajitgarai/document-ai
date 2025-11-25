"""History API endpoints for fetching user's documents and query history."""
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.history import Document, QueryHistory
from src.models.history_schemas import DocumentResponse, QueryHistoryResponse
from src.services.security import get_current_active_user
from src.database import get_db

router = APIRouter(prefix="/history")


@router.get("/documents", response_model=list[DocumentResponse])
async def get_user_documents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Get all documents uploaded by the current user."""
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.uploaded_at.desc()).all()
    
    return documents


@router.get("/queries", response_model=list[QueryHistoryResponse])
async def get_user_query_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get query history for the current user."""
    history = db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id
    ).order_by(QueryHistory.created_at.desc()).limit(limit).all()
    
    return history
