from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.config import settings
from core.logger import setup_logger
from services.vector_store import VectorStoreService

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
        self._setup_prompts()
    
    def _setup_prompts(self):
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are an assistant for the GIK Institute (GIKI) website. Answer the question based on the context provided.
            If the context doesn't contain the information needed, say you don't know based on the provided documents.
            Be concise and accurate in your response.
            
            Context: {context}
            
            Question: {question}
            
            Answer:
            """
        )
        
        self.self_knowledge_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
            You are an assistant for the GIK Institute (GIKI) website. 
            Determine if you can answer the following question using your general knowledge about GIKI.
            Questions about GIKI programs, history, faculty, or general information are appropriate.
            Do not answer questions about weather, unrelated topics, etc.
            
            Question: {question}
            
            Respond with "YES" if you can answer from your knowledge, "NO" if you need to search documents.
            """
        )
    
    def _can_answer_from_knowledge(self, question: str) -> bool:
        try:
            chain = self.self_knowledge_prompt | self.llm | self.output_parser
            response = chain.invoke({"question": question})
            return "YES" in response.upper()
        except Exception as e:
            logger.error(f"Error in knowledge check: {e}")
            return False
    
    def _retrieve_context(self, question: str) -> str:
        try:
            results = self.vector_store.search(question, top_k=settings.TOP_K)
            context_parts = []
            for result in results:
                if result['distance'] < settings.CONTEXT_THRESHOLD:
                    context_parts.append(result['content'])
            return "\n\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
    
    def generate_response(self, question: str) -> str:
        try:
            # Check if we can answer from general knowledge
            if self._can_answer_from_knowledge(question):
                # Use general LLM knowledge for GIKI-related questions
                chain = self.rag_prompt | self.llm | self.output_parser
                context = self._retrieve_context(question)
                return chain.invoke({"context": context, "question": question})
            else:
                # Check if question is relevant to GIKI
                if any(keyword in question.lower() for keyword in 
                      ['giki', 'gik institute', 'gandhara', 'computer science', 'engineering', 'admission', 'campus', 'student', 'faculty']):
                    # Retrieve context and answer
                    context = self._retrieve_context(question)
                    if context:
                        chain = self.rag_prompt | self.llm | self.output_parser
                        return chain.invoke({"context": context, "question": question})
                    else:
                        return "I couldn't find relevant information in the documents to answer your question about GIKI."
                else:
                    return "This system is designed to answer questions specifically about GIK Institute. Please ask a question related to GIKI."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "An error occurred while processing your request. Please try again."