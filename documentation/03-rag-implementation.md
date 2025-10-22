# 🤖 RAG Implementation

## Overview

The RAG (Retrieval-Augmented Generation) system combines semantic search with conversational AI to provide accurate, context-aware responses about GIKI.

## 🔧 Core RAG Service

### RAG Service Architecture (`app/services/rag_service.py`)

**Main orchestrator** that handles the complete RAG pipeline:

```python
class RAGService:
    def __init__(self):
        # Initialize LLM (Google Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_TOKENS
        )
        
        # Initialize vector store
        self.vector_store = VectorStoreService()
        
        # Initialize caching and session management
        self.cache = {}
        self.sessions = {}
        self.cache_ttl = 600  # 10 minutes
```

### Query Processing Pipeline

```python
def generate_response_with_history(self, question: str, session_id: str, history: list = []):
    # 1. Check response cache
    cache_key = self._cache_key(question, session_id)
    cached = self._get_cache(cache_key)
    if cached:
        return cached, history
    
    # 2. Retrieve relevant context
    context, confidence = self._get_context(question)
    
    # 3. Format conversation history
    formatted_history = self._format_history(history)
    
    # 4. Generate response with LLM
    answer = self._generate_llm_response(context, question, formatted_history)
    
    # 5. Update session and cache
    updated_history = self._update_session(session_id, question, answer, history)
    self._set_cache(cache_key, answer)
    
    return answer, updated_history
```

### Context Retrieval

```python
def _get_context(self, question: str):
    try:
        # Search vector store for relevant documents
        results = self.vector_store.search(question, top_k=settings.TOP_K)
        
        if not results:
            return "", 1.0
        
        # Calculate confidence based on similarity scores
        distances = [r["distance"] for r in results]
        avg_distance = sum(distances) / len(distances)
        
        # Combine retrieved documents
        context = "\n\n".join([r["content"] for r in results])
        
        return context, avg_distance
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return "", 1.0
```

### Prompt Engineering

**Carefully crafted prompt** for optimal responses:

```python
def _setup_prompt(self):
    self.prompt = PromptTemplate(
        input_variables=["context", "question", "history"],
        template="""
        You are an expert assistant for the Ghulam Ishaq Khan Institute of Engineering Sciences, Pakistan (GIKI).
        Use the retrieved context below to answer the user's question if it helps.
        If the context is irrelevant or incomplete, rely on your own general knowledge.
        Always be concise, factually accurate, and friendly.
        Do not answer with long paragraphs, be brief and consistent with your answers.
        
        Previous conversation:
        {history}
        
        Context:
        {context}

        Question:
        {question}

        Answer:
        """
    )
```

## 🔍 Vector Store Service

### ChromaDB Integration (`app/services/vector_store.py`)

**Semantic search interface** with ChromaDB:

```python
class VectorStoreService:
    def __init__(self):
        self.client = chromadb.CloudClient(
            api_key=settings.CHROMA_DB_API_KEY,
            tenant=settings.CHROMA_TENANT,
            database=settings.CHROMA_DATABASE
        )
        
        self.collection = self.client.get_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=OpenAIEmbeddingFunction()
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Format results for RAG service
            return self._format_search_results(results)
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
```

### Search Result Processing

```python
def _format_search_results(self, results):
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
```

## 💬 Conversation Memory

### Session Management

**Maintains context** across conversation turns:

```python
def _format_history(self, history: list) -> str:
    if not history:
        return "No previous conversation history."
    
    formatted = []
    # Use last 5 exchanges to stay within context limits
    for item in history[-5:]:
        formatted.append(f"User: {item['question']}")
        formatted.append(f"Assistant: {item['answer']}")
    
    return "\n".join(formatted)

def _update_session(self, session_id: str, question: str, answer: str, history: list):
    # Add new Q&A to history
    updated_history = history + [{"question": question, "answer": answer}]
    
    # Keep only last 10 exchanges to prevent memory issues
    if len(updated_history) > 10:
        updated_history = updated_history[-10:]
    
    # Store in session cache
    self.sessions[session_id] = updated_history
    
    return updated_history
```

### Caching Strategy

**Response caching** for performance:

```python
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
```

## 🌐 FastAPI Backend

### API Implementation (`app/main.py`)

**RESTful API** with FastAPI:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="GIKI RAG API",
    description="Retrieval Augmented Generation API for GIK Institute Information",
    version="1.0.0"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()
```

### Request/Response Models

```python
class QueryRequest(BaseModel):
    question: str
    session_id: str
    history: list = []

class QueryResponse(BaseModel):
    question: str
    answer: str
    status: str = "success"
    session_id: str
    history: list = []
```

### Main Query Endpoint

```python
@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    try:
        answer, updated_history = rag_service.generate_response_with_history(
            request.question, 
            request.session_id,
            request.history
        )
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            session_id=request.session_id,
            history=updated_history
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "GIKI RAG API"}
```

## 🎨 Frontend Implementation

### Chat Interface (`app/templates/index.html`)

**WhatsApp-style UI** with real-time messaging:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GIKI Assistant</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav>
        <div class="navbar">
            <img class="dpimg" src="/static/images/giki.png" alt="GIKI Logo">
            <div class="personalInfo">
                <label id="name">GIKI Assistant</label>
                <label id="lastseen">Online</label>
            </div>
        </div>
    </nav>

    <div class="scrollable" id="myScrollable">
        <div id="chatting" class="chatting">
            <ul id="listUL">
                <!-- Messages will be added here dynamically -->
            </ul>
        </div>
    </div>

    <footer>
        <div class="sendBar">
            <input id="inputMSG" type="text" placeholder="Ask me anything about GIKI..." autofocus>
            <svg onclick="sendMsg()" viewBox="0 0 24 24">
                <path fill="currentColor" d="M1.101 21.757 23.8 12.028 1.101 2.3l.011 7.912 13.623 1.816-13.623 1.817-.011 7.912z"></path>
            </svg>
        </div>
    </footer>

    <script src="/static/js/script.js"></script>
</body>
</html>
```

### JavaScript Chat Logic (`app/static/js/script.js`)

**Real-time messaging** with session management:

```javascript
let sessionId = generateSessionId();
let conversationHistory = [];

async function sendMsg() {
    const input = document.getElementById('inputMSG');
    const question = input.value.trim();
    
    if (!question) return;
    
    // Add user message to chat
    addMessage(question, 'user');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question: question,
                session_id: sessionId,
                history: conversationHistory
            })
        });
        
        const data = await response.json();
        
        // Update conversation history
        conversationHistory = data.history;
        
        // Add assistant response
        hideTypingIndicator();
        addMessage(data.answer, 'assistant');
        
    } catch (error) {
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    }
}

function addMessage(text, sender) {
    const chatList = document.getElementById('listUL');
    const messageElement = document.createElement('li');
    messageElement.className = sender === 'user' ? 'sent' : 'receive';
    messageElement.innerHTML = `<p>${text}</p>`;
    chatList.appendChild(messageElement);
    
    // Scroll to bottom
    document.getElementById('myScrollable').scrollTop = 
        document.getElementById('myScrollable').scrollHeight;
}
```

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export CHROMA_DB_API_KEY="your_key"

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

```bash
# Using Gunicorn for production
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ⚡ Performance Features

### Response Optimization
- **Caching**: 10-minute TTL for common queries
- **Session Management**: Efficient memory usage
- **Batch Processing**: Optimized database queries
- **Async Operations**: Non-blocking I/O

### Scalability Features
- **Stateless Design**: Easy horizontal scaling
- **Connection Pooling**: Efficient database connections
- **Load Balancing**: Multiple worker processes
- **Resource Management**: Memory and CPU optimization

### Quality Assurance
- **Confidence Scoring**: Context relevance assessment
- **Fallback Responses**: Graceful error handling
- **Input Validation**: Pydantic schema validation
- **Logging**: Comprehensive error tracking

---

**Next**: [Operations Guide](04-operations-guide.md)