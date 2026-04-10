"""
Kết nối Qdrant (Local Mode - Không cần Docker)
"""

from qdrant_client import QdrantClient
import os
from config import config

_qdrant_client = None


def get_qdrant_client():
    """Get or create Qdrant client instance"""
    global _qdrant_client
    
    if _qdrant_client is None:
        # Tạo thư mục lưu trữ nếu chưa có
        os.makedirs(config.QDRANT_DATA_PATH, exist_ok=True)
        
        # Kết nối Qdrant ở local mode
        _qdrant_client = QdrantClient(path=config.QDRANT_DATA_PATH)
        print(f"✅ Connected to Qdrant (local mode)")
        print(f"   📁 Storage: {os.path.abspath(config.QDRANT_DATA_PATH)}")
        print(f"   📁 Collection: {config.QDRANT_COLLECTION_NAME}")
    
    return _qdrant_client


def get_collection_info():
    """Get information about the collection"""
    client = get_qdrant_client()
    collection_name = config.QDRANT_COLLECTION_NAME
    
    if client.collection_exists(collection_name):
        info = client.get_collection(collection_name)
        return {
            'name': collection_name,
            'points_count': info.points_count,
            'vector_size': info.config.params.vectors.size
        }
    return None


def collection_exists():
    """Check if collection exists"""
    client = get_qdrant_client()
    return client.collection_exists(config.QDRANT_COLLECTION_NAME)