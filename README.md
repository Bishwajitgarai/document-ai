# FastAPI RAG System with LangChain & Google Gemini

A production-ready RAG (Retrieval-Augmented Generation) system built with FastAPI, LangChain, and Google Gemini. Upload code files (.py, .js, .java, etc.) and query them using natural language with AI-powered responses.

## Features

- 📤 **File Upload**: Upload code files in various formats (.py, .js, .java, .cpp, .go, .rs, .txt, .md)
- 🔍 **Smart Chunking**: Language-aware code splitting for optimal retrieval
- 🧠 **Vector Search**: ChromaDB for efficient similarity search
- 💬 **RAG Queries**: Ask questions and get Gemini-powered answers with source citations
- 🐳 **Docker Support**: Easy deployment with Docker Compose
- 📦 **UV Package Manager**: Fast and reliable dependency management
- 🤖 **Google Gemini**: Powered by Google's Gemini 1.5 Flash for fast, intelligent responses

## Architecture

```
┌─────────────┐
│   FastAPI   │
└──────┬──────┘
       │
   ┌───┴────────────────┬──────────────┐
   │                    │              │
┌──▼───────┐    ┌──────▼─────┐  ┌────▼─────┐
│ Upload   │    │   Query    │  │  Health  │
│ Endpoint │    │  Endpoint  │  │  Check   │
└──┬───────┘    └──────┬─────┘  └──────────┘
   │                   │
   └────────┬──────────┘
            │
    ┌───────▼────────┐
    │   Document     │
    │   Processor    │
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │  Vector Store  │
    │   (ChromaDB)   │
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │   RAG Engine   │
    │   (LangChain)  │
    └────────────────┘
```

## Prerequisites

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) package manager
- Docker & Docker Compose (for containerized deployment)
- Google API key (required for Gemini LLM - get one at https://aistudio.google.com/apikey)

## Installation

### Using UV (Recommended)

1. **Clone the repository**
   ```bash
   cd /path/to/project
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY for AI-generated answers
   ```

4. **Run the application**
   ```bash
   uv run uvicorn src.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Using Docker Compose

1. **Build and run**
   ```bash
   docker-compose up --build
   ```

2. **Run in background**
   ```bash
   docker-compose up -d
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Upload File

Upload a code file for processing and storage.

**Endpoint**: `POST /upload`

**Example with curl**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@example.py"
```

**Example with Python**:
```python
import requests

with open("example.py", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
print(response.json())
```

**Response**:
```json
{
  "status": "success",
  "filename": "example.py",
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "chunks_created": 5,
  "message": "File uploaded and processed successfully. Created 5 chunks."
}
```

### 2. Query Documents

Ask questions about uploaded documents.

**Endpoint**: `POST /query`

**Example with curl**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the main function do?",
    "k": 4
  }'
```

**Example with Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What does the main function do?",
        "k": 4
    }
)
print(response.json())
```

**Response**:
```json
{
  "query": "What does the main function do?",
  "answer": "The main function initializes the FastAPI application and sets up...",
  "sources": [
    {
      "content": "def main():\n    app = FastAPI()...",
      "metadata": {
        "filename": "example.py",
        "file_type": ".py",
        "document_id": "123e4567-e89b-12d3-a456-426614174000"
      }
    }
  ]
}
```

### 3. Health Check

Check if the service is running.

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

## Configuration

Environment variables can be set in `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | None | Google API key for Gemini LLM (required) |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHROMA_PERSIST_DIRECTORY` | `./chroma_data` | ChromaDB storage location |
| `UPLOAD_DIRECTORY` | `./uploads` | Uploaded files storage |
| `MAX_FILE_SIZE` | `10485760` | Max file size (10MB) |
| `CHUNK_SIZE` | `1000` | Text chunk size |
| `CHUNK_OVERLAP` | `200` | Chunk overlap size |
| `RETRIEVAL_K` | `4` | Number of documents to retrieve |
| `LLM_MODEL` | `gemini-1.5-flash` | Gemini model to use (also: `gemini-1.5-pro`) |

## Supported File Types

- **Python**: `.py`
- **JavaScript**: `.js`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`
- **Go**: `.go`
- **Rust**: `.rs`
- **Text**: `.txt`, `.md`

## How It Works

1. **Upload**: Files are uploaded, validated, and split into chunks using language-specific splitters
2. **Embedding**: Each chunk is converted to a vector embedding using HuggingFace models
3. **Storage**: Embeddings are stored in ChromaDB for fast similarity search
4. **Query**: When you ask a question:
   - Your query is embedded using the same model
   - Similar document chunks are retrieved via vector search
   - Retrieved context is sent to Google Gemini to generate an intelligent answer
   - Answer and sources are returned

## Development

### Project Structure

```
.
├── src/
│   ├── api/
│   │   ├── upload.py          # File upload endpoint
│   │   └── query.py           # Query endpoint
│   ├── services/
│   │   ├── document_processor.py  # Document chunking
│   │   ├── vector_store.py        # ChromaDB operations
│   │   └── rag_engine.py          # RAG query logic
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── config.py              # Configuration
│   └── main.py                # FastAPI app
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests (when implemented)
uv run pytest
```

## Docker Commands

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### No AI-generated answers

If you see a warning message instead of AI-generated answers, you need to set the `GOOGLE_API_KEY` environment variable:

```bash
export GOOGLE_API_KEY=your-google-api-key-here
# or add to .env file
```

**Get your free Google API key**: Visit https://aistudio.google.com/apikey

### Embeddings downloading slowly

The first time you run the app, it downloads the embedding model (~90MB). This is cached for future runs.

### Port already in use

If port 8000 is already in use, modify the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Use port 8080 instead
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
