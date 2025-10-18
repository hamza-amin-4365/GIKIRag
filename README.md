# 🎓 GIKI RAG Assistant

> **Intelligent Q&A system for Ghulam Ishaq Khan Institute of Engineering Sciences & Technology**

A modern RAG (Retrieval-Augmented Generation) chatbot that provides accurate, context-aware answers about GIKI programs, admissions, faculty, and campus life.

---

## ✨ Features

<div align="center">

| 🧠 **Smart AI** | 💬 **Conversation Memory** | ⚡ **Fast Search** | 🎨 **Clean UI** |
|:---:|:---:|:---:|:---:|
| Powered by Google Gemini | Remembers chat context | ChromaDB vector search | WhatsApp-style interface |

</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API Keys (see configuration below)

### 1️⃣ Clone & Install
```bash
git clone <your-repo-url>
cd gikirag
pip install -r requirements.txt
```

### 2️⃣ Environment Setup
Create a `.env` file in the root directory:

```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_API_KEY=your_chromadb_api_key_here

# ChromaDB Configuration
CHROMA_TENANT=your_tenant_id
CHROMA_DATABASE=gikirag
CHROMA_COLLECTION_NAME=giki_collection
```

### 3️⃣ Run the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000`

---

## 🔧 API Configuration

### 🔑 Getting API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Google Gemini** | AI Language Model | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **OpenAI** | Text Embeddings | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **ChromaDB** | Vector Database | [ChromaDB Cloud](https://www.trychroma.com/) |

---

## 📁 Project Structure

```
gikirag/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── logger.py        # Logging setup
│   ├── services/
│   │   ├── rag_service.py   # RAG logic & conversation memory
│   │   └── vector_store.py  # ChromaDB integration
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── data/                    # GIKI website content (markdown)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🎯 Usage Examples

### Chat Interface
Ask natural questions about GIKI:

```
👤 "What AI programs does GIKI offer?"
🤖 "GIKI offers several AI-related programs including..."

👤 "What are the admission requirements?"
🤖 "For the AI programs mentioned earlier, the requirements are..."
```

### API Endpoint
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Tell me about GIKI computer science program"}'
```

---

## ⚙️ Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `TOP_K` | 5 | Number of documents to retrieve |
| `TEMPERATURE` | 0.1 | AI response creativity (0-1) |
| `MAX_TOKENS` | 1024 | Maximum response length |
| `LOG_LEVEL` | INFO | Logging verbosity |

---

## 🔄 Conversation Memory

The assistant remembers your conversation context:
- **Session-based**: Each browser session maintains separate history
- **Smart Context**: Last 3 Q&A pairs kept for relevance
- **Memory Management**: Auto-cleanup prevents memory bloat

---

## 🛠️ Development

### Running in Development
```bash
# With auto-reload
uvicorn app.main:app --reload

# Custom port
uvicorn app.main:app --port 3000
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 📊 Performance Features

- ✅ **Response Caching** - Faster repeated queries
- ✅ **Vector Search** - Semantic document retrieval  
- ✅ **Context Scoring** - Confidence-based responses
- ✅ **Session Management** - Efficient memory usage

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **API Key Error** | Check `.env` file and key validity |
| **ChromaDB Connection** | Verify tenant/database settings |
| **Port Already in Use** | Use different port: `--port 3000` |
| **Module Not Found** | Run `pip install -r requirements.txt` |

### Support
- 📧 Create an issue on GitHub
- 💬 Check existing issues for solutions

---

<div align="center">

**Made with ❤️ for GIKI Community**

[🌟 Star this repo](../../stargazers) • [🐛 Report Bug](../../issues) • [💡 Request Feature](../../issues)

</div>