"""Document processing service for chunking and text extraction."""
import os
from pathlib import Path
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language,
)
from langchain_core.documents import Document

from src.config import get_settings


class DocumentProcessor:
    """Handle document loading and chunking."""
    
    def __init__(self):
        self.settings = get_settings()
        self.language_map = {   
                # Python
                ".py": Language.PYTHON,
                ".pyw": Language.PYTHON,
                ".pyx": Language.PYTHON,
                
                # JavaScript/TypeScript
                ".js": Language.JS,
                ".jsx": Language.JS,
                ".mjs": Language.JS,
                ".ts": Language.TS,
                ".tsx": Language.TS,
                
                # Java/Kotlin/Scala
                ".java": Language.JAVA,
                ".kt": Language.KOTLIN,
                ".kts": Language.KOTLIN,
                # ".scala": Language.SCALAR,
                # ".sc": Language.SCALAR,
                
                # C/C++
                ".cpp": Language.CPP,
                ".cc": Language.CPP,
                ".cxx": Language.CPP,
                ".c++": Language.CPP,
                ".hpp": Language.CPP,
                ".h": Language.CPP,  # Could be C or C++
                ".c": Language.C,
                
                # Go
                ".go": Language.GO,
                
                # Rust
                ".rs": Language.RUST,
                
                # Ruby
                ".rb": Language.RUBY,
                ".erb": Language.RUBY,
                ".gemfile": Language.RUBY,
                
                # PHP
                ".php": Language.PHP,
                ".phtml": Language.PHP,
                ".php4": Language.PHP,
                ".php5": Language.PHP,
                
                # C#
                ".cs": Language.CSHARP,
                
                # Swift
                ".swift": Language.SWIFT,
                
                # Markdown & Documentation
                ".md": Language.MARKDOWN,
                ".markdown": Language.MARKDOWN,
                ".rst": Language.RST,
                
                # HTML/Web
                ".html": Language.HTML,
                ".htm": Language.HTML,
                ".xhtml": Language.HTML,
                
                # Shell/PowerShell
                # ".sh": Language.TEXT,  # or create SHELL enum
                # ".bash": Language.TEXT,
                # ".zsh": Language.TEXT,
                ".ps1": Language.POWERSHELL,
                ".psm1": Language.POWERSHELL,
                
                # Other languages
                ".lua": Language.LUA,
                ".pl": Language.PERL,
                ".pm": Language.PERL,
                ".hs": Language.HASKELL,
                ".lhs": Language.HASKELL,
                ".ex": Language.ELIXIR,
                ".exs": Language.ELIXIR,
                ".sol": Language.SOL,
                ".cob": Language.COBOL,
                ".cbl": Language.COBOL,
                ".vb": Language.VISUALBASIC6,
                ".bas": Language.VISUALBASIC6,
                
                # Text files
                # ".txt": Language.TEXT,
                # ".text": Language.TEXT,
                
                # LaTeX
                ".tex": Language.LATEX,
                ".latex": Language.LATEX,
                
                # Protocol Buffers
                ".proto": Language.PROTO,
            }
        
    

            

    
    
    def read_file(self, file_path: str) -> str:
        """Read file content as text."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
    
    def get_text_splitter(self, file_extension: str) -> RecursiveCharacterTextSplitter:
        """Get appropriate text splitter based on file type."""
        language = self.language_map.get(file_extension)
        
        if language:
            # Use language-specific splitter for code
            return RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
            )
        else:
            # Use generic splitter for text files
            return RecursiveCharacterTextSplitter(
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
                separators=["\n\n", "\n", " ", ""],
            )
    
    def process_file(self, file_path: str, filename: str) -> list[Document]:
        """Process a file into chunks."""
        # Read file content
        content = self.read_file(file_path)
        
        # Get file extension
        file_extension = Path(filename).suffix.lower()
        
        # Get appropriate splitter
        text_splitter = self.get_text_splitter(file_extension)
        
        # Create chunks
        chunks = text_splitter.create_documents(
            texts=[content],
            metadatas=[{
                "filename": filename,
                "source": file_path,
                "file_type": file_extension,
            }]
        )
        
        return chunks
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        """Validate file extension and size."""
        file_extension = Path(filename).suffix.lower()
        
        # Check extension
        if file_extension not in self.language_map.keys():
            return False, f"File type {file_extension} not allowed. Allowed types: {self.settings.allowed_extensions}"
        
        # Check size
        if file_size > self.settings.max_file_size:
            max_mb = self.settings.max_file_size / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_mb}MB"
        
        return True, "Valid"
