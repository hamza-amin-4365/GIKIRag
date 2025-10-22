# 🎯 Project Overview & Architecture

## What is GIKI RAG?

GIKI RAG is an intelligent Q&A system for Ghulam Ishaq Khan Institute that combines AI language models with a comprehensive knowledge base to provide accurate, contextual answers about GIKI programs, admissions, faculty, and campus life.

## 🏗️ System Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Frontend  │───▶│  FastAPI     │───▶│   RAG Service   │
│   (HTML/JS) │    │   Backend    │    │                 │
└─────────────┘    └──────────────┘    └─────────────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                          ▼                     ▼                     ▼
                   ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
                   │  ChromaDB   │    │  Google Gemini  │    │   Session   │
                   │ Vector Store│    │      LLM        │    │   Manager   │
                   └─────────────┘    └─────────────────┘    └─────────────┘
```

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: LLM application framework
- **Google Gemini 2.5**: Language model for responses
- **OpenAI Embeddings**: Text-to-vector conversion
- **ChromaDB**: Vector database for semantic search

### Frontend
- **HTML5/CSS3**: Clean, responsive interface
- **Vanilla JavaScript**: Real-time chat functionality
- **WhatsApp-style UI**: Familiar user experience

### Data Pipeline
- **Crawl4AI**: Advanced web scraping
- **Python**: Data processing and chunking
- **Markdown**: Content format

## 📊 Key Components

### 1. RAG Service (`app/services/rag_service.py`)
**Core orchestrator** that handles:
- Query processing and context retrieval
- LLM prompt engineering
- Conversation memory management
- Response caching and optimization

```python
class RAGService:
    def generate_response_with_history(self, question, session_id, history):
        # 1. Check cache for quick responses
        # 2. Retrieve relevant context from vector store
        # 3. Format prompt with conversation history
        # 4. Generate response using Gemini LLM
        # 5. Update session memory and cache
```

### 2. Vector Store Service (`app/services/vector_store.py`)
**Search engine** that provides:
- Semantic similarity search
- Document retrieval and ranking
- ChromaDB integration
- Custom embedding functions

### 3. Web Scraper (`scripts/crawler.py`)
**Data collector** that:
- Discovers URLs from GIKI sitemaps
- Crawls pages in parallel (5 concurrent)
- Extracts clean content using CSS selectors
- Converts to markdown format

### 4. Vector Database Builder (`scripts/build_vectorstore.py`)
**Data processor** that:
- Chunks text into 256-word segments with 25-word overlap
- Generates embeddings using OpenAI
- Stores in ChromaDB with rich metadata
- Handles batch processing and error recovery

## 🎯 Data Flow

### Query Processing
```
User Question → FastAPI → RAG Service → Vector Store → ChromaDB
                    ↓           ↓            ↓
              Session Cache ← LLM Service ← Context Retrieval
                    ↓
              Response → User
```

### Data Ingestion
```
GIKI Website → Web Scraper → Markdown Files → Text Chunker → 
Embeddings Generator → ChromaDB Vector Store
```

## 📈 Performance Features

### Conversation Memory
- **Session-based**: Each user maintains separate chat history
- **Context Window**: Last 5 Q&A pairs for relevance
- **Memory Management**: Auto-cleanup prevents bloat

### Caching Strategy
- **Response Cache**: 10-minute TTL for common queries
- **Session Cache**: In-memory conversation storage
- **Vector Cache**: ChromaDB built-in caching

### Optimization
- **Parallel Processing**: Concurrent web scraping
- **Batch Operations**: Efficient database operations
- **Async Operations**: Non-blocking I/O where possible

## 🔒 Security & Configuration

### Environment Variables
```bash
# Required API Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
CHROMA_DB_API_KEY=your_chroma_key

# ChromaDB Settings
CHROMA_TENANT=your_tenant_id
CHROMA_DATABASE=gikirag
CHROMA_COLLECTION_NAME=giki_collection

# RAG Parameters
TOP_K=5                    # Documents to retrieve
TEMPERATURE=0.1            # LLM creativity (0-1)
MAX_TOKENS=1024           # Response length limit
```

### Security Features
- Input validation with Pydantic
- API key management via environment
- CORS configuration for web access
- Error message sanitization

## 📊 Project Metrics

### Data Coverage
- **575+** web pages scraped
- **2,847** text chunks created
- **456K+** total words processed
- **5** content categories (academics, faculty, news, admissions, admin)

### Performance Targets
- **< 3 seconds**: Average response time
- **95%+**: Accuracy for GIKI queries
- **100+**: Concurrent users supported
- **99.9%**: System uptime goal

## 🎯 Use Cases

### Student Queries
- "What AI programs does GIKI offer?"
- "What are the admission requirements for CS?"
- "Who teaches machine learning courses?"

### Faculty Information
- "Tell me about Dr. Smith's research areas"
- "What courses are offered in Fall 2024?"
- "How do I contact the admissions office?"

### Campus Information
- "What facilities are available on campus?"
- "When is the next orientation session?"
- "What are the hostel policies?"

---

**Next**: [Data Pipeline](02-data-pipeline.md)