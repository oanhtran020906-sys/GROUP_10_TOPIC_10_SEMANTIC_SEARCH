from typing import List, Optional, Union
import numpy as np
import logging
from PIL import Image
import requests
from io import BytesIO
import base64

# Try to import CLIP model
try:
    from sentence_transformers import SentenceTransformer
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logging.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageEmbeddingService:
    """
    Service for generating image embeddings using CLIP model
    Supports multimodal search (text-to-image and image-to-image)
    """
    
    def __init__(self):
        self.dimension = 512
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load CLIP model for image embeddings"""
        if not CLIP_AVAILABLE:
            logger.error("CLIP model not available. Install sentence-transformers")
            return
        
        try:
            # Use CLIP model from sentence-transformers
            logger.info("Loading CLIP model for image embeddings...")
            self.model = SentenceTransformer('clip-ViT-B-32')
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ CLIP model loaded (dimension: {self.dimension})")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            self.model = None
    
    def get_image_embedding_from_path(self, image_path: str) -> Optional[List[float]]:
        """
        Generate embedding from image file path
        
        Args:
            image_path: Path to image file
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.model:
            logger.error("CLIP model not loaded")
            return None
        
        try:
            image = Image.open(image_path)
            return self._get_embedding(image)
        except Exception as e:
            logger.error(f"Failed to process image from path: {e}")
            return None
    
    def get_image_embedding_from_url(self, image_url: str) -> Optional[List[float]]:
        """
        Generate embedding from image URL
        
        Args:
            image_url: URL of the image
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.model:
            return None
        
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content))
            return self._get_embedding(image)
        except Exception as e:
            logger.error(f"Failed to process image from URL: {e}")
            return None
    
    def get_image_embedding_from_base64(self, base64_string: str) -> Optional[List[float]]:
        """
        Generate embedding from base64 encoded image
        
        Args:
            base64_string: Base64 encoded image string
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.model:
            return None
        
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            return self._get_embedding(image)
        except Exception as e:
            logger.error(f"Failed to process base64 image: {e}")
            return None
    
    def get_image_embedding_from_pil(self, image: Image.Image) -> Optional[List[float]]:
        """
        Generate embedding from PIL Image object
        
        Args:
            image: PIL Image object
        
        Returns:
            Embedding vector or None if failed
        """
        return self._get_embedding(image)
    
    def _get_embedding(self, image: Image.Image) -> Optional[List[float]]:
        """
        Internal method to generate embedding from PIL Image
        """
        if not self.model:
            return None
        
        try:
            # Convert RGBA to RGB if needed
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Resize image to model's expected size (optional, model handles it)
            # image = image.resize((224, 224))
            
            # Generate embedding
            embedding = self.model.encode(image)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate image embedding: {e}")
            return None
    
    def search_similar_images(
        self, 
        query_image: Union[str, Image.Image],
        qdrant_manager,
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> List[dict]:
        """
        Search for similar images using Qdrant
        
        Args:
            query_image: Image path, URL, or PIL Image
            qdrant_manager: QdrantManager instance
            limit: Max results
            score_threshold: Minimum similarity score
        
        Returns:
            List of similar products with scores
        """
        # Get embedding for query image
        if isinstance(query_image, str):
            if query_image.startswith('http'):
                embedding = self.get_image_embedding_from_url(query_image)
            else:
                embedding = self.get_image_embedding_from_path(query_image)
        else:
            embedding = self.get_image_embedding_from_pil(query_image)
        
        if embedding is None:
            logger.error("Failed to generate query image embedding")
            return []
        
        # Search in Qdrant using image vector
        results = qdrant_manager.search(
            query_vector=embedding,
            limit=limit,
            score_threshold=score_threshold,
            vector_name="image"  # For multimodal collections
        )
        
        return results
    
    def get_text_embedding_for_image_search(self, text_query: str) -> List[float]:
        """
        Generate text embedding using CLIP for text-to-image search
        
        Args:
            text_query: Text description to search for images
        
        Returns:
            Text embedding in CLIP space
        """
        if not self.model:
            logger.error("CLIP model not loaded")
            return [0.0] * self.dimension
        
        try:
            embedding = self.model.encode(text_query)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate text embedding for image search: {e}")
            return [0.0] * self.dimension

# Singleton instance
image_embedding_service = ImageEmbeddingService()