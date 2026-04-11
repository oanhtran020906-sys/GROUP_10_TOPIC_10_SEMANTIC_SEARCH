import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/semantic_search")

    #Qdrant
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "tech_products")
    QDRANT_DATA_PATH = os.getenv("QDRANT_DATA_PATH", "./qdrant_data")

    #Sentence-Transformers Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "keepitreal/vietnamese-sbert")
    
    VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 768))

    DATA_PATH = os.getenv("DATA_PATH", "backend/data/raw/products.csv")

    #API Server 
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

settings = Config()