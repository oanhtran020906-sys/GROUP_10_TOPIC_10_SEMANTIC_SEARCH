import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Qdrant Configuration
    QDRANT_DATA_PATH = os.getenv("QDRANT_DATA_PATH", "./qdrant_data")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "tech_products")
    
    # Sentence-Transformers Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 384))
    
    # File paths
    DATA_PATH = os.getenv("DATA_PATH", "data/raw/products.csv")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))

# Create config instance
config = Config()