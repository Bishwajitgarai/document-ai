"""Query endpoint for RAG."""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.models.schemas import QueryRequest, QueryResponse, Source
from src.models.user import User
from src.models.history import QueryHistory
from src.services.rag_engine import get_rag_engine
from src.services.security import get_current_active_user
from src.database import get_db

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Session = Depends(get_db)
):
    """
    Query the document store using RAG.
    
    This endpoint retrieves relevant document chunks and uses Google Gemini LLM to generate
    an answer based on the context.
    
    Note: Requires GOOGLE_API_KEY environment variable to be set for full RAG.
    If not set, will return relevant document chunks without LLM-generated answer.
    """
    try:
        # Get RAG engine
        rag_engine = get_rag_engine()
        
        # Query
        result = rag_engine.query(request.query, k=request.k)
        
        # Format sources
        sources = [
            Source(
                content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in result["source_documents"]
        ]
        
        # Save query history to database
        sources_json = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result["source_documents"]
        ]
        
        db_history = QueryHistory(
            user_id=current_user.id,
            query=request.query,
            answer=result["answer"],
            sources=sources_json
        )
        db.add(db_history)
        db.commit()
        
        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
