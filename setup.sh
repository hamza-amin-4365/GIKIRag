#!/bin/bash

echo "🚀 Setting up GIKI RAG Project..."

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

mkdir -p app/{core,services,static/{css,js,images},templates}
mkdir -p data/processed
mkdir -p logs

touch app/__init__.py

cat > .env << 'EOF'
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_API_KEY=your_chromadb_api_key_here
CHROMA_TENANT=your_tenant_id
CHROMA_DATABASE=gikirag
CHROMA_COLLECTION_NAME=giki_collection
TOP_K=5
TEMPERATURE=0.1
MAX_TOKENS=1024
LOG_LEVEL=INFO
EOF

echo "✅ Setup complete! Edit .env with your API keys and run: uvicorn app.main:app --reload"

