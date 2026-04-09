import sys
import os
import openai
from typing import List
import logging

# Thêm dòng này để import config từ thư mục cha
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextEmbeddingService:
    """Service for generating text embeddings using OpenAI API"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.TEXT_EMBEDDING_MODEL
        self.dimension = settings.TEXT_EMBEDDING_DIMENSION
        logger.info(f"✅ Using OpenAI model: {self.model_name} (dimension: {self.dimension})")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return [0.0] * self.dimension
        
        try:
            response = openai.embeddings.create(
                model=self.model_name,
                input=text[:8000],
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * self.dimension
    
    def get_product_embedding(self, product: dict) -> List[float]:
        """Generate embedding for a product"""
        text_parts = []
        
        if product.get('name'):
            text_parts.append(f"Sản phẩm: {product['name']}")
        
        if product.get('brand') and product['brand'] != 'Unknown':
            text_parts.append(f"Thương hiệu: {product['brand']}")
        
        if product.get('category'):
            text_parts.append(f"Danh mục: {product['category']}")
        
        if product.get('description'):
            desc = product['description'][:500]
            text_parts.append(f"Mô tả: {desc}")
        
        combined_text = " | ".join(text_parts)
        return self.get_embedding(combined_text)


# Singleton instance
embedding_service = TextEmbeddingService()