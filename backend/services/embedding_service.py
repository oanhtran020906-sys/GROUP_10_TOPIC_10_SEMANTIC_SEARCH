"""
Embedding Service sử dụng Sentence-Transformers 2.5.1
CHẠY LOCAL - MIỄN PHÍ - KHÔNG CẦN API KEY
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging
import sys
import os

# Thêm đường dẫn để import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service để tạo embeddings từ text sử dụng Sentence-Transformers
    Model mặc định: all-MiniLM-L6-v2 (384 dimensions, nhanh, nhẹ)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.model_name = config.EMBEDDING_MODEL
        self.model = None
        self.vector_size = config.VECTOR_SIZE
        
        self._load_model()
        self._initialized = True
    
    def _load_model(self):
        """Tải Sentence-Transformers model"""
        try:
            logger.info(f"📥 Loading Sentence-Transformers model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.vector_size = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ Model loaded successfully!")
            logger.info(f"   📐 Vector dimension: {self.vector_size}")
            logger.info(f"   💰 Cost: FREE (runs locally)")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Chuyển đổi text thành vector embedding
        
        Args:
            texts: Một hoặc nhiều chuỗi text
            normalize: Chuẩn hóa vector (cho cosine similarity)
        
        Returns:
            Numpy array của embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )
        
        return embeddings
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Lấy embedding cho một text"""
        return self.encode(text)[0]
    
    def get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Lấy embeddings cho nhiều text cùng lúc"""
        return self.encode(texts)
    
    def get_vector_size(self) -> int:
        """Trả về kích thước vector"""
        return self.vector_size
    
    def get_model_info(self) -> dict:
        """Trả về thông tin model"""
        return {
            'model_name': self.model_name,
            'vector_size': self.vector_size,
            'framework': 'Sentence-Transformers',
            'version': '2.5.1',
            'cost': 'FREE',
            'local': True
        }


# Singleton instance
embedding_service = EmbeddingService()