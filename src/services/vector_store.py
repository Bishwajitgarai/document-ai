"""Vector store service using ChromaDB."""
import os
from typing import List
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.config import get_settings


class VectorStoreService:
    """Manage vector store operations with ChromaDB."""
    
    def __init__(self):
        self.settings = get_settings()
        self._embeddings = None
        self._vector_store = None
        
        # Ensure persistence directory exists
        os.makedirs(self.settings.chroma_persist_directory, exist_ok=True)
    
    @property
    def embeddings(self):
        """Lazy load embeddings model."""
        if self._embeddings is None:
            print(f"Loading embedding model: {self.settings.embedding_model}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.settings.embedding_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings
    
    @property
    def vector_store(self) -> Chroma:
        """Lazy load vector store."""
        if self._vector_store is None:
            self._vector_store = Chroma(
                collection_name=self.settings.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.settings.chroma_persist_directory,
            )
        return self._vector_store
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store."""
        print(f"Adding {len(documents)} documents to vector store")
        ids = self.vector_store.add_documents(documents)
        return ids
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents."""
        print(f"Searching for: {query} (k={k})")
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def get_retriever(self, k: int = 4):
        """Get a retriever for RAG."""
        return self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.vector_store.delete_collection()
            self._vector_store = None
            print("Collection deleted successfully")
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            return self.vector_store._collection.count()
        except Exception:
            return 0


# Global instance
_vector_store_service = None


def get_vector_store_service() -> VectorStoreService:
    """Get singleton instance of vector store service."""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service
