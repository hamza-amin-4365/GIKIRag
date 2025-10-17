import os
import chromadb

from dotenv  import load_dotenv

load_dotenv()

client = chromadb.CloudClient(
  api_key=os.getenv("CHROMA_DB_API_KEY"),
  tenant='3a4f58b1-4505-4361-b7da-9cec61ef8a3f',
  database='gikirag'
)