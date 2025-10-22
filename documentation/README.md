# 📚 GIKI RAG Project Documentation

Complete documentation for the GIKI RAG (Retrieval-Augmented Generation) system - from data scraping to deployment.

## 📋 Documentation Structure

1. **[Project Overview & Architecture](01-overview-architecture.md)** - System design, tech stack, and components
2. **[Data Pipeline](02-data-pipeline.md)** - Web scraping, processing, and vector database setup  
3. **[RAG Implementation](03-rag-implementation.md)** - API development, frontend, and deployment
4. **[Operations Guide](04-operations-guide.md)** - Configuration, troubleshooting, and maintenance

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd gikirag
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the application
uvicorn app.main:app --reload
```

## 🎯 Key Features

- **Smart Q&A**: Context-aware responses about GIKI
- **Conversation Memory**: Maintains chat history
- **Fast Search**: Vector-based semantic retrieval
- **Clean UI**: WhatsApp-style interface
- **Scalable**: Handles multiple concurrent users

---

*Last updated: October 22, 2025*