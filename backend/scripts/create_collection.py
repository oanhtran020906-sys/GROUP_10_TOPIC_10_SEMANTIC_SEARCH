#!/usr/bin/env python
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.qdrant import init_qdrant
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_single_vector_collection():
    """Create collection for text-only embeddings"""
    logger.info("=" * 50)
    logger.info("Creating SINGLE VECTOR collection for text embeddings")
    logger.info("=" * 50)
    
    # Initialize Qdrant manager
    manager = init_qdrant(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name=settings.QDRANT_COLLECTION_NAME
    )
    
    # Create collection
    success = manager.create_collection(
        vector_size=settings.TEXT_EMBEDDING_DIMENSION,
        recreate_if_exists=False
    )
    
    if success:
        logger.info(f"✅ Collection '{settings.QDRANT_COLLECTION_NAME}' is ready!")
        # Get collection info
        info = manager.get_collection_info()
        logger.info(f"📊 Collection Info: {info}")
    else:
        logger.error("❌ Failed to create collection")
        sys.exit(1)

if __name__ == "__main__":
    create_single_vector_collection()