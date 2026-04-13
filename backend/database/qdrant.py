"""
Qdrant Vector Database Manager - Tối ưu cho Sentence-Transformers
"""

import os
import sys
import uuid
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    PayloadSchemaType
)
from dotenv import load_dotenv
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class QdrantVectorStore:
    """
    Qdrant Vector Database Manager
    Tự động lấy vector size từ embedding service
    """
    
    def __init__(self, embedding_service=None):
        """Khởi tạo kết nối đến Qdrant server"""
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333)),
            timeout=30
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.embedding_service = embedding_service
        self.vector_size = None
        
    def set_embedding_service(self, embedding_service):
        """Set embedding service để lấy vector size"""
        self.embedding_service = embedding_service
        if embedding_service:
            self.vector_size = embedding_service.vector_size
            logger.info(f"📐 Vector size từ embedding service: {self.vector_size}")
        
    def init_collection(self, recreate: bool = False):
        """Khởi tạo collection với vector size phù hợp"""
        if not self.vector_size:
            raise ValueError("Chưa set embedding_service hoặc vector_size chưa được xác định")
        
        # Kiểm tra collection tồn tại
        collections = self.client.get_collections().collections
        exists = self.collection_name in [c.name for c in collections]
        
        if exists and recreate:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"🗑️ Đã xóa collection cũ: {self.collection_name}")
            exists = False
        
        if not exists:
            # Tạo collection với cấu hình cho semantic search
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                    on_disk=True
                ),
                hnsw_config={
                    "m": 16,
                    "ef_construct": 100,
                    "full_scan_threshold": 10000
                }
            )
            logger.info(f"✅ Đã tạo collection '{self.collection_name}' với size={self.vector_size}")
            
            # Tạo payload indexes
            self._create_payload_indexes()
        else:
            logger.info(f"ℹ️ Collection '{self.collection_name}' đã tồn tại")
            
    def _create_payload_indexes(self):
        """Tạo index cho metadata fields"""
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="category",
                field_schema=PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="price",
                field_schema=PayloadSchemaType.FLOAT
            )
            logger.info("✅ Đã tạo payload indexes")
        except Exception as e:
            logger.warning(f"⚠️ Không thể tạo index: {e}")
    
    def insert_product(self, product_id: int, vector: List[float], metadata: Dict[str, Any]):
        """Insert một sản phẩm vào vector database"""
        try:
            if len(vector) != self.vector_size:
                raise ValueError(f"Vector size {len(vector)} != {self.vector_size}")
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=product_id,
                        vector=vector,
                        payload=metadata
                    )
                ]
            )
            return True
        except Exception as e:
            logger.error(f"❌ Insert failed for {product_id}: {e}")
            return False
    
    def insert_batch(self, products_data: List[Tuple[int, List[float], Dict[str, Any]]]):
        """Insert batch sản phẩm"""
        points = []
        for product_id, vector, metadata in products_data:
            if len(vector) == self.vector_size:
                points.append(
                    PointStruct(
                        id=product_id,
                        vector=vector,
                        payload=metadata
                    )
                )
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"✅ Batch inserted {len(points)} products")
    
    def semantic_search(
        self, 
        query_vector: List[float], 
        limit: int = 4,
        category_filter: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Semantic search với query vector và filters"""
        # Xây dựng filter
        must_conditions = []
        
        if category_filter:
            must_conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category_filter)
                )
            )
        
        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range["gte"] = min_price
            if max_price is not None:
                price_range["lte"] = max_price
            must_conditions.append(
                FieldCondition(
                    key="price",
                    range=Range(**price_range)
                )
            )
        
        qdrant_filter = Filter(must=must_conditions) if must_conditions else None
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qdrant_filter,
            score_threshold=score_threshold,
            with_payload=True
        )
        
        # Format kết quả
        formatted_results = []
        for hit in results:
            formatted_results.append({
                "product_id": hit.payload.get("product_id", hit.id),
                "name": hit.payload.get("name"),
                "description": hit.payload.get("description"),
                "category": hit.payload.get("category"),
                "price": hit.payload.get("price"),
                "image_path": hit.payload.get("image_path"),
                "similarity_score": round(hit.score, 4),
                "budget_id": hit.payload.get("budget_id"),
                "similarity_percent": round(hit.score * 100, 1)
            })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Lấy thống kê collection"""
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            "name": self.collection_name,
            "vector_size": self.vector_size,
            "points_count": info.points_count,
            "status": "healthy"
        }

# Khởi tạo (sẽ set embedding service sau)
qdrant_store = QdrantVectorStore()