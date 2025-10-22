# 🔄 Data Pipeline

## Overview

The data pipeline transforms GIKI website content into a searchable vector database through web scraping, content processing, and embedding generation.

## 🕷️ Web Scraping

### Scraper Implementation (`scripts/crawler.py`)

**Technology**: Crawl4AI with AsyncWebCrawler for modern, efficient scraping.

```python
# Key scraping configuration
browser_config = BrowserConfig(
    headless=True,
    extra_args=["--disable-gpu", "--no-sandbox"]
)

config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(),
    excluded_tags=['footer', 'nav', 'header'],
    css_selector='#kingster-page-wrapper',  # Main content area
    exclude_external_links=True,
    cache_mode=CacheMode.ENABLED
)
```

### URL Discovery Strategy

**Sitemap-based approach** for comprehensive coverage:

```python
def get_all_sitemap_urls() -> List[str]:
    sitemap_urls = []
    
    # Academic content
    for i in range(1, 4):
        sitemap_urls.append(f"https://giki.edu.pk/page-sitemap{i}.xml")
    
    # Course information  
    for i in range(1, 5):
        sitemap_urls.append(f"https://giki.edu.pk/course-sitemap{i}.xml")
    
    # Faculty profiles
    for i in range(1, 3):
        sitemap_urls.append(f"https://giki.edu.pk/personnel-sitemap{i}.xml")
    
    # Events and news
    sitemap_urls.append("https://giki.edu.pk/tribe_events-sitemap.xml")
    sitemap_urls.append("https://giki.edu.pk/category-sitemap.xml")
    
    return get_sitemap_urls_from_list(sitemap_urls)
```

### Parallel Processing

**Concurrent crawling** with rate limiting:

```python
async def crawl_parallel(urls: List[str], max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)  # Limit concurrent requests
    
    async def process_url(url: str):
        async with semaphore:
            result = await crawler.arun(url=url, config=config)
            if result.success:
                # Save as markdown file
                filename = url_to_filename(url)
                save_content(filename, result.markdown)
```

### Scraping Results

| Content Type | Pages | Size | Description |
|--------------|-------|------|-------------|
| Academic Programs | 150+ | 2.5MB | Course descriptions, requirements |
| Faculty Profiles | 200+ | 1.8MB | Bio, research areas, contact info |
| News & Events | 100+ | 1.2MB | Announcements, schedules |
| Admissions | 50+ | 800KB | Requirements, procedures |
| Administration | 75+ | 600KB | Policies, services |
| **Total** | **575+** | **6.9MB** | **Comprehensive GIKI content** |

## 📝 Data Processing

### Text Chunking Strategy (`scripts/build_vectorstore.py`)

**Sentence-based chunking** for semantic coherence:

```python
def chunk_text(text: str, chunk_size: int = 256, overlap: int = 25) -> List[str]:
    """Split text into overlapping chunks."""
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
            
            # Create overlap from last few sentences
            overlap_chunk = create_overlap(current_chunk, overlap)
            current_chunk = overlap_chunk + [sentence]
            current_length = len(" ".join(current_chunk).split())
    
    return chunks
```

**Chunking Parameters**:
- **Chunk Size**: 256 words (optimal for embeddings)
- **Overlap**: 25 words (maintains context)
- **Method**: Sentence-based (preserves meaning)

### Metadata Extraction

**Rich metadata** for enhanced search:

```python
def process_document(file_path: str) -> List[Dict[str, Any]]:
    # Extract content and metadata
    url = reconstruct_url_from_filename(file_path)
    title = extract_title_from_content(content)
    category = classify_content_category(file_path)
    
    # Create chunks with metadata
    for i, chunk in enumerate(chunks):
        doc_id = hashlib.md5(f"{url}_chunk_{i}".encode()).hexdigest()
        
        metadata = {
            "url": url,
            "title": title,
            "category": category,
            "chunk_id": i,
            "source_file": Path(file_path).name,
            "word_count": len(chunk.split())
        }
```

### Content Categories

| Category | Description | Example URLs |
|----------|-------------|--------------|
| `academics` | Programs, courses, curriculum | `/course/`, `/academics/` |
| `faculty` | Staff profiles, research | `/personnel/`, `/faculty/` |
| `news_events` | News, events, announcements | `/event/`, `/news/` |
| `admissions` | Admission info, requirements | `/admissions/`, `/apply/` |
| `administration` | Policies, services | `/administration/`, `/services/` |

## 🎯 Vector Database Setup

### ChromaDB Configuration

**Cloud-based vector storage** with OpenAI embeddings:

```python
# Initialize ChromaDB client
client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_DB_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)

# Create collection with custom embedding function
collection = client.create_collection(
    name="giki_collection",
    embedding_function=OpenAIEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"}  # Cosine similarity
)
```

### Custom Embedding Function

**OpenAI text-embedding-3-small** for cost-effective performance:

```python
class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.max_batch_size = 2048  # API limit
    
    def __call__(self, texts: Documents) -> Embeddings:
        all_embeddings = []
        
        # Process in batches to respect API limits
        for i in range(0, len(texts), self.max_batch_size):
            batch = texts[i:i + self.max_batch_size]
            
            response = self.client.embeddings.create(
                input=batch,
                model=self.model_name
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
```

### Batch Ingestion Strategy

**Efficient batch processing** with error handling:

```python
def ingest_documents_batch(collection, documents: List[Dict], batch_size: int = 50):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        try:
            collection.add(
                ids=[doc["id"] for doc in batch],
                documents=[doc["content"] for doc in batch],
                metadatas=[doc["metadata"] for doc in batch]
            )
            print(f"✅ Batch {i//batch_size + 1}: Added {len(batch)} documents")
            
        except Exception as e:
            print(f"❌ Batch failed: {e}")
            # Retry with smaller batches
            retry_smaller_batches(collection, batch)
```

## 🚀 Running the Pipeline

### Step 1: Web Scraping

```bash
cd scripts
python crawler.py
```

**Output**: Raw markdown files in `data/raw/`

### Step 2: Vector Database Build

```bash
python build_vectorstore.py
```

**Process**:
1. Read all markdown files from `data/raw/`
2. Process and chunk content
3. Generate embeddings using OpenAI
4. Store in ChromaDB with metadata

### Expected Results

```
🚀 Starting vector database build process...
📁 Found 575 markdown files to process

📊 Processing Statistics:
Total documents: 2,847
Total words: 456,789
Average chunk size: 160.4 words
Files processed: 575
Categories: {
    'academics': 1,245,
    'faculty': 687,
    'news_events': 423,
    'admissions': 298,
    'administration': 194
}

💾 Ingesting 2,847 documents into ChromaDB...
✅ Ingestion complete!
```

## 🔍 Quality Control

### Data Validation

```python
def validate_document(doc: Dict[str, Any]) -> bool:
    # Check required fields
    required_fields = ["id", "content", "metadata"]
    if not all(field in doc for field in required_fields):
        return False
    
    # Content validation
    content = doc["content"]
    if not content or len(content.strip()) < 20:
        return False
    
    # Metadata validation
    metadata = doc["metadata"]
    required_metadata = ["url", "title", "category"]
    return all(field in metadata for field in required_metadata)
```

### Deduplication

```python
def deduplicate_documents(documents: List[Dict]) -> List[Dict]:
    seen_hashes = set()
    unique_docs = []
    
    for doc in documents:
        content_hash = hashlib.md5(doc["content"].encode()).hexdigest()
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_docs.append(doc)
    
    return unique_docs
```

## ⚡ Performance Optimization

### Scraping Optimization
- **Concurrent Requests**: 5 parallel crawlers
- **Caching**: Avoid re-crawling same URLs
- **Rate Limiting**: Respectful server interaction
- **Error Handling**: Retry with exponential backoff

### Processing Optimization
- **Batch Processing**: 50 documents per batch
- **Memory Management**: Process files incrementally
- **Error Recovery**: Retry failed batches with smaller sizes
- **Progress Tracking**: Real-time processing updates

### Database Optimization
- **Cosine Similarity**: Optimal for text embeddings
- **Batch Ingestion**: Efficient API usage
- **Connection Reuse**: Minimize connection overhead
- **Index Optimization**: HNSW for fast similarity search

---

**Next**: [RAG Implementation](03-rag-implementation.md)