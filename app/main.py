from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.logger import setup_logger
from app.services.rag_service import RAGService

logger = setup_logger(__name__)
app = FastAPI(
    title="GIKI RAG API",
    description="Retrieval Augmented Generation API for GIK Institute Information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
try:
    rag_service = RAGService()
    logger.info("RAG service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG service: {e}")
    raise

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    status: str = "success"

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello from GIKIRAG_API!"})

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    try:
        answer = rag_service.generate_response(request.question)
        return QueryResponse(
            question=request.question,
            answer=answer
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "GIKI RAG API"}