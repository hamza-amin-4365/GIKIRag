import os
import chromadb
from dotenv import load_dotenv
from pathlib import Path
import re
from typing import List, Dict, Any
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import hashlib
from openai import OpenAI

load_dotenv()

class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
    
    def __call__(self, texts: Documents) -> Embeddings:
        # Handle empty input
        if not texts:
            return []
        
        # Process in batches of 2048 to stay within API limits
        batch_size = 2048
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.model_name
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings

def chunk_text(text: str, chunk_size: int = 256, overlap: int = 25) -> List[str]:
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        
        if current_length + sentence_length <= chunk_size:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            # Create overlapping chunk
            temp_chunk = []
            temp_length = 0
            for s in reversed(current_chunk[-3:]):
                s_len = len(s.split())
                if temp_length + s_len <= overlap:
                    temp_chunk.insert(0, s)
                    temp_length += s_len
                else:
                    break
            
            current_chunk = temp_chunk + [sentence]
            current_length = temp_length + sentence_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def get_category_from_path(file_path: str) -> str:
    parts = Path(file_path).parts
    for part in parts:
        if part in ['pages', 'courses', 'faculty', 'tribe_events', 'news', 'admin']:
            return part
    return 'others'

def process_document(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract URL from filename
    filename = Path(file_path).stem
    url = filename.replace('_', '/').replace('giki_edu_pk', 'https://giki.edu.pk').strip('/')
    url = re.sub(r'/+', '/', url)  # Replace multiple slashes with single slash
    if not url.startswith('http'):
        url = 'https://' + url
    
    # Extract title from content if available
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else Path(file_path).stem.replace('_', ' ').title()
    
    # Chunk the content
    chunks = chunk_text(content)
    
    documents = []
    for i, chunk in enumerate(chunks):
        doc_id = hashlib.md5(f"{url}_chunk_{i}".encode()).hexdigest()
        metadata = {
            "url": url,
            "title": title,
            "category": get_category_from_path(file_path),
            "chunk_id": i,
            "source_file": Path(file_path).name
        }
        documents.append({
            "id": doc_id,
            "content": chunk,
            "metadata": metadata
        })
    
    return documents

def build_vector_db(data_dir: str = "../data/raw"):
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_DB_API_KEY"),
        tenant='3a4f58b1-4505-4361-b7da-9cec61ef8a3f',
        database='gikirag'
    )
    
    try:
        collection = client.get_collection("giki_collection")
    except:
        collection = client.create_collection(
            name="giki_collection",
            embedding_function=OpenAIEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"}
        )
    
    # Get all markdown files
    md_files = list(Path(data_dir).rglob("*.md"))
    print(f"Found {len(md_files)} markdown files to process")
    
    all_docs = []
    all_metadatas = []
    all_ids = []
    
    for file_path in md_files:
        try:
            docs = process_document(str(file_path))
            for doc in docs:
                all_ids.append(doc["id"])
                all_docs.append(doc["content"])
                all_metadatas.append(doc["metadata"])
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    print(f"Total documents to add: {len(all_docs)}")
    
    # Add documents to collection in smaller batches to avoid quota limits
    batch_size = 50  # Reduced batch size to avoid document size limits
    for i in range(0, len(all_docs), batch_size):
        batch_docs = all_docs[i:i+batch_size]
        batch_metadatas = all_metadatas[i:i+batch_size]
        batch_ids = all_ids[i:i+batch_size]
        
        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents")
        except Exception as e:
            print(f"Error adding batch {i//batch_size + 1}: {e}")
            # Retry with smaller batch size if needed
            if len(batch_docs) > 10:
                mid = len(batch_docs) // 2
                try:
                    collection.add(
                        documents=batch_docs[:mid],
                        metadatas=batch_metadatas[:mid],
                        ids=batch_ids[:mid]
                    )
                    print(f"  Retried first half: {len(batch_docs[:mid])} documents")
                except Exception as e2:
                    print(f"  Retry failed for first half: {e2}")
                
                try:
                    collection.add(
                        documents=batch_docs[mid:],
                        metadatas=batch_metadatas[mid:],
                        ids=batch_ids[mid:]
                    )
                    print(f"  Retried second half: {len(batch_docs[mid:])} documents")
                except Exception as e3:
                    print(f"  Retry failed for second half: {e3}")

if __name__ == "__main__":
    build_vector_db()