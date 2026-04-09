import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, Range
from typing import List, Dict, Optional, Any
import logging
import requests

# Thêm dòng này để import config từ thư mục cha
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantManager:
    """Manager for Qdrant vector database operations"""
    
    def __init__(self, host: str, port: int, collection_name: str):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        logger.info(f"✅ Connected to Qdrant at {host}:{port}")
    
    def collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            collections = self.client.get_collections().collections
            return any(col.name == self.collection_name for col in collections)
        except Exception as e:
            logger.error(f"Failed to check collection: {e}")
            return False
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"✅ Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    def create_collection(self, vector_size: int = 1536) -> bool:
        """Create a new collection"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"✅ Created collection '{self.collection_name}' with size {vector_size}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """Get collection statistics"""
        try:
            url = f"http://{self.host}:{self.port}/collections/{self.collection_name}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})
                return {
                    "name": self.collection_name,
                    "status": result.get('status', 'unknown'),
                    "vectors_count": result.get('vectors_count', 0),
                    "points_count": result.get('points_count', 0)
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def upsert_points(self, points: List[PointStruct], batch_size: int = 50) -> bool:
        """Insert or update points"""
        if not points:
            return True
        
        try:
            total = len(points)
            for i in range(0, total, batch_size):
                batch = points[i:i+batch_size]
                self.client.upsert(collection_name=self.collection_name, points=batch)
                logger.info(f"📤 Upserted {min(i+batch_size, total)}/{total} points")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points: {e}")
            return False
    
    def search(self, query_vector: List[float], limit: int = 10, score_threshold: float = 0.5) -> List[Any]:
        """Search for similar vectors"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


# Global instance
qdrant_manager: Optional[QdrantManager] = None

def init_qdrant(host: str, port: int, collection_name: str) -> QdrantManager:
    global qdrant_manager
    qdrant_manager = QdrantManager(host, port, collection_name)
    return qdrant_manager

def get_qdrant_manager() -> QdrantManager:
    if qdrant_manager is None:
        raise Exception("Qdrant manager not initialized")
    return qdrant_manager