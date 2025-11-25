"""FastAPI application main entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from src.config import get_settings
from src.models.schemas import HealthResponse
from src.api import upload, query, auth, history
from src.database import engine, Base

# Get settings
settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="RAG system for document upload and querying using LangChain with user authentication",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (dashboard)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(query.router, tags=["Query"])
app.include_router(history.router, tags=["History"])


@app.get("/")
async def root():
    """Redirect to dashboard."""
    return RedirectResponse(url="/static/index.html")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version="0.1.0"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

