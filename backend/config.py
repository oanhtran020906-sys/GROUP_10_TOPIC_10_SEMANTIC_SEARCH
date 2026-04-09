import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    """Application settings"""
    
    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "laptop_products")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TEXT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    TEXT_EMBEDDING_DIMENSION: int = 1536
    
    # App Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    def __init__(self):
        logger.info(f"Qdrant Host: {self.QDRANT_HOST}")
        logger.info(f"Qdrant Port: {self.QDRANT_PORT}")
        logger.info(f"Collection Name: {self.QDRANT_COLLECTION_NAME}")
        logger.info(f"Embedding Dimension: {self.TEXT_EMBEDDING_DIMENSION}")
        if not self.OPENAI_API_KEY or self.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
            logger.error("❌ OPENAI_API_KEY not set! Please add your API key to .env file")
        else:
            logger.info("✅ OpenAI API Key loaded")

settings = Settings()