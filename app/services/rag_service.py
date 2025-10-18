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
        self.sessions = {}  # New: Store session history
        self._setup_prompt()

    def _setup_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["context", "question", "history"],
            template="""
            You are an expert assistant for the Ghulam Ishaq Khan Institute of Engineering Sciences, Pakistan (GIKI).
            Use the retrieved context below to answer the user's question if it helps.
            If the context is irrelevant or incomplete, rely on your own general knowledge.
            Always be concise, factually accurate, and friendly.
            Do not answer with long paragraphs, be breif and consistent with your answers.
            
            Previous conversation:
            {history}
            
            Context:
            {context}

            Question:
            {question}

            Answer:
            """
        )

    def _format_history(self, history: list) -> str:
        if not history:
            return "No previous conversation history."
        formatted = []
        for item in history[-5:]:  # Use last 5 exchanges
            formatted.append(f"User: {item['question']}")
            formatted.append(f"Assistant: {item['answer']}")
        return "\n".join(formatted)

    def _cache_key(self, question: str, session_id: str) -> str:
        combined = question.strip().lower() + session_id
        return hashlib.sha256(combined.encode()).hexdigest()

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
        # For backward compatibility - create a temporary session
        session_id = "temp_session"
        answer, _ = self.generate_response_with_history(question, session_id)
        return answer

    # Updated method for handling chat history with session management
    def generate_response_with_history(self, question: str, session_id: str, history: list = []) -> tuple[str, list]:
        key = self._cache_key(question, session_id)
        cached = self._get_cache(key)
        if cached:
            return cached, history
        
        # Get session history if not provided
        if not history:
            history = self.sessions.get(session_id, [])
        
        try:
            context, avg_distance = self._get_context(question)
            context = context or "No relevant context found."
            formatted_history = self._format_history(history)
            
            prompt = self.prompt
            chain = prompt | self.llm | self.output_parser
            
            if avg_distance > 0.7:
                logger.info("Low context confidence, relying more on model knowledge.")
            elif avg_distance > 0.4:
                logger.info("Partial context confidence, blending sources.")
            else:
                logger.info("High context confidence, using retrieval.")
            
            answer = chain.invoke({
                "context": context, 
                "question": question, 
                "history": formatted_history
            })
            
            # Update session history
            updated_history = history + [{"question": question, "answer": answer}]
            # Keep only last 10 exchanges to prevent memory issues
            if len(updated_history) > 10:
                updated_history = updated_history[-10:]
            
            # Store in session
            self.sessions[session_id] = updated_history
            
            self._set_cache(key, answer)
            return answer, updated_history
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_msg = "I encountered an issue generating your answer. Please try again."
            updated_history = history + [{"question": question, "answer": error_msg}]
            if len(updated_history) > 10:
                updated_history = updated_history[-10:]
            self.sessions[session_id] = updated_history
            return error_msg, updated_history