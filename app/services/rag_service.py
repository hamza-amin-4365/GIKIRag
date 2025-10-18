import time
import hashlib
from app.core.config import settings
from app.core.logger import setup_logger
from app.services.vector_store import VectorStoreService

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI


logger = setup_logger(__name__)

class RAGService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        self.vector_store = VectorStoreService()
        self.output_parser = StrOutputParser()
        self.cache = {}
        self.cache_ttl = 600
        self._setup_prompt()

    def _setup_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are an expert assistant for the Ghulam Ishaq Khan Institute of Engineering Sciences, Pakistan (GIKI).
            Use the retrieved context below to answer the user's question if it helps.
            If the context is irrelevant or incomplete, rely on your own general knowledge.
            Always be concise, factually accurate, and friendly.

            Context:
            {context}

            Question:
            {question}

            Answer:
            """
        )

    def _cache_key(self, question: str) -> str:
        return hashlib.sha256(question.strip().lower().encode()).hexdigest()

    def _get_cache(self, key: str):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None

    def _set_cache(self, key: str, value: str):
        self.cache[key] = (value, time.time())

    def _process_results(self, results):
        if not results:
            return "", 1.0
        distances = [r["distance"] for r in results]
        avg_distance = sum(distances) / len(distances)
        context = "\n\n".join([r["content"] for r in results])
        return context, avg_distance

    def _get_context(self, question: str):
        try:
            results = self.vector_store.search(question, top_k=settings.TOP_K)
            context, avg_distance = self._process_results(results)
            return context, avg_distance
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return "", 1.0

    def generate_response(self, question: str) -> str:
        key = self._cache_key(question)
        cached = self._get_cache(key)
        if cached:
            return cached
        try:
            context, avg_distance = self._get_context(question)
            context = context or "No relevant context found."
            prompt = self.prompt
            chain = prompt | self.llm | self.output_parser
            if avg_distance > 0.7:
                logger.info("Low context confidence, relying more on model knowledge.")
            elif avg_distance > 0.4:
                logger.info("Partial context confidence, blending sources.")
            else:
                logger.info("High context confidence, using retrieval.")
            answer = chain.invoke({"context": context, "question": question})
            self._set_cache(key, answer)
            return answer
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I encountered an issue generating your answer. Please try again."