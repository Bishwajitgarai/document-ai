"""RAG engine for query processing."""
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

from src.config import get_settings
from src.services.vector_store import get_vector_store_service


class RAGEngine:
    """RAG engine for question answering."""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_store_service = get_vector_store_service()
    
    def _get_llm(self):
        """Get LLM instance (requires Google API key)."""
        if not self.settings.google_api_key:
            raise ValueError(
                "Google API key not configured. "
                "Please set GOOGLE_API_KEY environment variable."
            )
        
        return ChatGoogleGenerativeAI(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            google_api_key=self.settings.google_api_key,
        )
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents into a single string."""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def query(self, query: str, k: int = 4) -> dict:
        """Query the RAG system."""
        try:
            # Retrieve relevant documents
            docs = self.vector_store_service.similarity_search(query, k=k)
            
            # Get LLM
            llm = self._get_llm()
            
            # Format context from documents
            context = self._format_docs(docs)
            
            # Create prompt
            prompt_template = ChatPromptTemplate.from_template(
                """You are a helpful AI assistant analyzing code and documents.
Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context, just say so - don't make up an answer.

Context:
{context}

Question: {question}

Provide a clear and detailed answer based on the context above:"""
            )
            
            # Format the prompt
            messages = prompt_template.format_messages(
                context=context,
                question=query
            )
            
            # Get answer from LLM
            response = llm.invoke(messages)
            
            return {
                "answer": response.content,
                "source_documents": docs
            }
        
        except ValueError as e:
            # Handle Google API key error
            if "Google API key" in str(e):
                # Fallback: just return relevant documents without LLM
                docs = self.vector_store_service.similarity_search(query, k=k)
                return {
                    "answer": "⚠️ Google API key not configured. Showing relevant context only. "
                             "To get AI-generated answers, please set GOOGLE_API_KEY environment variable.",
                    "source_documents": docs
                }
            raise
    
    def query_without_llm(self, query: str, k: int = 4) -> List[Document]:
        """Query without LLM - just retrieve relevant documents."""
        return self.vector_store_service.similarity_search(query, k=k)


# Global instance
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get singleton instance of RAG engine."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
