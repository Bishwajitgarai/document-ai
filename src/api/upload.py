"""File upload endpoint."""
import os
import uuid
from typing import Annotated
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from src.config import get_settings
from src.models.schemas import UploadResponse
from src.models.user import User
from src.models.history import Document
from src.services.document_processor import DocumentProcessor
from src.services.vector_store import get_vector_store_service
from src.services.security import get_current_active_user
from src.database import get_db

router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Session = Depends(get_db)
):
    """
    Upload a file for processing and storage in the vector database.
    
    Supported file types: .py, .js, .java, .cpp, .c, .go, .rs, .txt, .md
    Maximum file size: 10MB
    """
    try:
        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Validate file
        is_valid, message = processor.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_directory, exist_ok=True)
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file
        file_extension = Path(file.filename).suffix
        saved_filename = f"{document_id}{file_extension}"
        file_path = os.path.join(settings.upload_directory, saved_filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process file into chunks
        chunks = processor.process_file(file_path, file.filename)
        
        # Add document ID to metadata
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
        
        # Store in vector database
        vector_store = get_vector_store_service()
        vector_store.add_documents(chunks)
        
        # Save document metadata to database
        db_document = Document(
            user_id=current_user.id,
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            chunks_created=len(chunks)
        )
        db.add(db_document)
        db.commit()
        
        return UploadResponse(
            status="success",
            filename=file.filename,
            document_id=document_id,
            chunks_created=len(chunks),
            message=f"File uploaded and processed successfully. Created {len(chunks)} chunks."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
