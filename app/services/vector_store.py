from typing import List, Dict, Any
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from core.config import settings
from core.logger import setup_logger

logger = setup_logger(__name__)

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = "models/embedding-001"

    def __call__(self, texts: Documents) -> Embeddings:
        if not texts:
            return []
        
        embeddings = []
        
        for text in texts:
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=text
                )
                embeddings.append(response["embedding"])
            except Exception as e:
                logger.error(f"Error embedding text: {e}")
                embeddings.append([0.0] * 768)
        
        return embeddings

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
                embedding_function=GeminiEmbeddingFunction()
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