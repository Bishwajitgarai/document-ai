from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Settings
    app_name: str = "RAG FastAPI"
    debug: bool = True
    
    # Google Gemini Settings
    google_api_key: str | None = None
    
    # Embedding Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector Store Settings
    chroma_persist_directory: str = "./chroma_data"
    collection_name: str = "documents"
    
    # File Upload Settings
    upload_directory: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Chunking Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # RAG Settings
    retrieval_k: int = 4  # Number of documents to retrieve
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.0
    
    # Authentication Settings
    database_url: str = "sqlite:///./rag_users.db"
    jwt_secret_key: str = "your-secret-key-change-in-production-please-use-a-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
