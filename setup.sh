#!/bin/bash

echo "🚀 Setting up GIKI RAG Project..."

# Create main project directory
# mkdir -p giki-rag-project
# cd giki-rag-project

# Core application structure
mkdir -p app/{core,routers,services,models}
touch app/__init__.py
touch app/main.py

# Core modules
touch app/core/__init__.py
touch app/core/config.py
touch app/core/logger.py  # Optional: you can leave empty or add basic logging later

# Services (RAG logic)
touch app/services/__init__.py
touch app/services/rag_service.py
touch app/services/vector_store.py

# Routers (API endpoints)
touch app/routers/__init__.py
touch app/routers/rag_router.py

# Models (Pydantic models)
touch app/models/__init__.py
touch app/models/query_models.py

# Data directories (your crawl4ai output goes here)
mkdir -p data/raw          # Your crawler outputs MD files here
mkdir -p data/processed    # Optional: if you preprocess before vectorizing
mkdir -p data/vectorstore  # ChromaDB will auto-create here

# Scripts directory (for your crawler and utilities)
mkdir -p scripts/
touch scripts/__init__.py
touch scripts/crawler.py   
touch scripts/build_vectorstore.py  # Script to load MD → chunk → embed → store

# Root level files
touch .env

# Create .env (basic config)
cat > .env << 'EOF'
HOST=127.0.0.1
PORT=8000
VECTOR_STORE_PATH=./data/vectorstore
EMBEDDING_MODEL=all-MiniLM-L6-v2
LOG_LEVEL=INFO
EOF

