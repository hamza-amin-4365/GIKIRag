from typing import List, Dict, Any
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from openai import OpenAI
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def __call__(self, texts: Documents) -> Embeddings:
        if not texts:
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error embedding text with OpenAI: {e}")
            # Fallback: zero vector same dimension (1536)
            return [[0.0] * 1536 for _ in texts]

class VectorStoreService:
    def __init__(self):
        try:
            self.client = chromadb.CloudClient(
                api_key=settings.CHROMA_DB_API_KEY,
                tenant=settings.CHROMA_TENANT,
                database=settings.CHROMA_DATABASE
            )
            self.collection = self.client.get_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                embedding_function= OpenAIEmbeddingFunction()
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            formatted_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                formatted_results.append({
                    'content': doc,
                    'metadata': meta,
                    'distance': dist
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []