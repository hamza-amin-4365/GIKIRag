# 🛠️ Operations Guide

## Configuration Management

### Environment Setup

**Required API Keys**:
```bash
# .env file configuration
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_API_KEY=your_chromadb_api_key_here

# ChromaDB Configuration
CHROMA_TENANT=your_tenant_id
CHROMA_DATABASE=gikirag
CHROMA_COLLECTION_NAME=giki_collection

# RAG Parameters
TOP_K=5                    # Number of documents to retrieve
TEMPERATURE=0.1            # LLM creativity (0-1)
MAX_TOKENS=1024           # Maximum response length
LOG_LEVEL=INFO            # Logging verbosity
```

### Getting API Keys

| Service | Purpose | How to Get |
|---------|---------|------------|
| **Google Gemini** | Language Model | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| **OpenAI** | Text Embeddings | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **ChromaDB** | Vector Database | [ChromaDB Cloud](https://www.trychroma.com/) |

### Configuration Class (`app/core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str
    CHROMA_DB_API_KEY: str
    
    # ChromaDB Settings
    CHROMA_TENANT: str
    CHROMA_DATABASE: str = "gikirag"
    CHROMA_COLLECTION_NAME: str = "giki_collection"
    
    # RAG Parameters
    TOP_K: int = 5
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1024
    
    # Application Settings
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 🚀 Deployment Options

### 1. Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd gikirag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

### 3. Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose**:
```yaml
version: '3.8'

services:
  giki-rag:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CHROMA_DB_API_KEY=${CHROMA_DB_API_KEY}
      - CHROMA_TENANT=${CHROMA_TENANT}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### 4. Cloud Deployment (AWS/GCP/Azure)

**Example for AWS EC2**:
```bash
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start

# Clone and deploy
git clone <your-repo-url>
cd gikirag
sudo docker-compose up -d
```

## 📊 Monitoring & Logging

### Logging Configuration (`app/core/logger.py`)

```python
import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
```

### Health Check Endpoint

```python
@app.get("/health")
def health_check():
    try:
        # Test vector store connection
        test_result = rag_service.vector_store.search("test", top_k=1)
        
        return {
            "status": "healthy",
            "service": "GIKI RAG API",
            "vector_store": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Usage
@monitor_performance
def generate_response_with_history(self, question, session_id, history):
    # Function implementation
    pass
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Errors

**Problem**: `Invalid API key` or `Authentication failed`

**Solutions**:
```bash
# Check if API keys are set
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
echo $CHROMA_DB_API_KEY

# Verify .env file exists and has correct format
cat .env

# Test API keys individually
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### 2. ChromaDB Connection Issues

**Problem**: `Connection refused` or `Tenant not found`

**Solutions**:
```python
# Test ChromaDB connection
import chromadb

try:
    client = chromadb.CloudClient(
        api_key="your_api_key",
        tenant="your_tenant",
        database="gikirag"
    )
    print("✅ ChromaDB connection successful")
except Exception as e:
    print(f"❌ ChromaDB connection failed: {e}")
```

#### 3. Memory Issues

**Problem**: `Out of memory` during processing

**Solutions**:
```python
# Reduce batch size in build_vectorstore.py
batch_size = 25  # Instead of 50

# Limit conversation history
MAX_HISTORY_LENGTH = 5  # Instead of 10

# Clear cache periodically
def clear_old_cache(self):
    current_time = time.time()
    expired_keys = [
        key for key, (_, timestamp) in self.cache.items()
        if current_time - timestamp > self.cache_ttl
    ]
    for key in expired_keys:
        del self.cache[key]
```

#### 4. Slow Response Times

**Problem**: Responses taking > 5 seconds

**Solutions**:
```python
# Enable response caching
ENABLE_CACHING = True
CACHE_TTL = 600  # 10 minutes

# Reduce TOP_K for faster retrieval
TOP_K = 3  # Instead of 5

# Use smaller embedding model
EMBEDDING_MODEL = "text-embedding-3-small"  # Instead of large
```

### Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `500` | Internal server error | Check logs, verify API keys |
| `422` | Validation error | Check request format |
| `429` | Rate limit exceeded | Implement backoff, check quotas |
| `503` | Service unavailable | Check ChromaDB connection |

### Debugging Commands

```bash
# Check application logs
tail -f logs/app.log

# Test API endpoint
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What programs does GIKI offer?", "session_id": "test"}'

# Check health status
curl http://localhost:8000/health

# Monitor resource usage
htop
df -h
free -m
```

## 🔄 Maintenance

### Regular Tasks

#### 1. Update Vector Database

```bash
# Re-scrape GIKI website (monthly)
cd scripts
python crawler.py

# Rebuild vector database
python build_vectorstore.py
```

#### 2. Monitor Performance

```python
# Add performance metrics
def get_system_metrics():
    return {
        "cache_size": len(rag_service.cache),
        "active_sessions": len(rag_service.sessions),
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent()
    }
```

#### 3. Log Rotation

```bash
# Setup logrotate for application logs
sudo nano /etc/logrotate.d/gikirag

# Content:
/path/to/gikirag/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 user user
}
```

### Backup Strategy

```bash
# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)

# Backup processed data
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### Security Updates

```bash
# Update dependencies regularly
pip list --outdated
pip install -r requirements.txt --upgrade

# Security scan
pip-audit

# Update base Docker image
docker pull python:3.9-slim
docker build -t gikirag:latest .
```

## 📈 Performance Tuning

### Optimization Settings

```python
# Optimal configuration for production
class ProductionSettings(Settings):
    TOP_K: int = 3                    # Faster retrieval
    TEMPERATURE: float = 0.1          # Consistent responses
    MAX_TOKENS: int = 512            # Shorter responses
    CACHE_TTL: int = 1800            # 30-minute cache
    MAX_HISTORY_LENGTH: int = 5      # Limited memory
    BATCH_SIZE: int = 25             # Smaller batches
```

### Scaling Recommendations

| Users | Configuration | Resources |
|-------|---------------|-----------|
| 1-10 | Single worker | 1 CPU, 2GB RAM |
| 10-50 | 2-4 workers | 2 CPU, 4GB RAM |
| 50-100 | 4-8 workers | 4 CPU, 8GB RAM |
| 100+ | Load balancer + multiple instances | 8+ CPU, 16GB+ RAM |

---

This completes the comprehensive yet concise documentation for the GIKI RAG project. The documentation covers all essential aspects from architecture to operations in just 4 focused files.