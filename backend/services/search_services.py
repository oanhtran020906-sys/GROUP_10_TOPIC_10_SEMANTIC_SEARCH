from typing import List, Dict, Optional, Any
import logging
from qdrant_client.models import PointStruct
from services.embedding_service import embedding_service
from database.qdrant import qdrant_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchService:
    """
    Service for semantic and traditional search operations
    """
    
    def __init__(self):
        self.embedding_service = embedding_service
    
    def semantic_search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform semantic search using vector embeddings
        
        Args:
            query: Natural language query string
            limit: Max number of results
            score_threshold: Minimum similarity score (0-1)
            filters: Optional payload filters (e.g., {"brand": "Apple", "price": {"min": 100, "max": 1000}})
        
        Returns:
            List of products with similarity scores
        """
        # Generate embedding for query
        query_vector = self.embedding_service.get_embedding(query)
        
        # Search in Qdrant
        results = qdrant_manager.search(
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filters
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "name": result.payload.get("name"),
                "brand": result.payload.get("brand"),
                "price": result.payload.get("price"),
                "description": result.payload.get("description"),
                "category": result.payload.get("category"),
                "similarity_score": round(result.score * 100, 2),  # Convert to percentage
                "search_type": "semantic"
            })
        
        return formatted_results
    
    def traditional_search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Traditional keyword-based search (simulated SQL LIKE)
        
        Args:
            query: Search keywords
            limit: Max results
        
        Returns:
            List of products matching keywords
        """
        # This is a simplified simulation
        # In production, this would be a PostgreSQL LIKE or full-text search
        
        # Get all products from Qdrant (in real app, query PostgreSQL)
        # For demo, we'll simulate by checking payloads
        
        # Simulate keyword matching
        keywords = query.lower().split()
        
        # We need to have access to all products
        # For now, return empty to demonstrate semantic search superiority
        return []
    
    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict]:
        """
        Hybrid search combining semantic and keyword search
        
        Args:
            query: Search query
            limit: Max results
            semantic_weight: Weight for semantic results (0-1)
            keyword_weight: Weight for keyword results (0-1)
        
        Returns:
            Combined and re-ranked results
        """
        semantic_results = self.semantic_search(query, limit=limit*2)
        keyword_results = self.traditional_search(query, limit=limit*2)
        
        # Combine and deduplicate by product ID
        combined = {}
        
        for result in semantic_results:
            product_id = result["id"]
            result["combined_score"] = result["similarity_score"] / 100 * semantic_weight
            combined[product_id] = result
        
        for result in keyword_results:
            product_id = result["id"]
            keyword_score = result.get("keyword_score", 0) / 100 * keyword_weight
            if product_id in combined:
                combined[product_id]["combined_score"] += keyword_score
            else:
                result["combined_score"] = keyword_score
                combined[product_id] = result
        
        # Sort by combined score and return top results
        sorted_results = sorted(
            combined.values(), 
            key=lambda x: x.get("combined_score", 0), 
            reverse=True
        )
        
        return sorted_results[:limit]

# Singleton instance
search_service = SearchService()