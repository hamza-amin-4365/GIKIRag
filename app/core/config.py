import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    # ChromaDB Settings
    CHROMA_DB_API_KEY: str = os.getenv("CHROMA_DB_API_KEY")
    CHROMA_TENANT: str = os.getenv("CHROMA_TENANT", "3a4f58b1-4505-4361-b7da-9cec61ef8a3f")
    CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "gikirag")
    CHROMA_COLLECTION_NAME: str = "giki_collection"
    
    # RAG Settings
    TOP_K: int = 5
    CONTEXT_THRESHOLD: float = 0.5
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.1
    
    # Application Settings
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()