from typing import List, Dict, Optional, Any
import logging
from database.postgres import get_db_connection, release_db_connection
from services.embedding_service import embedding_service
from database.qdrant import qdrant_manager

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.embedding_service = embedding_service

    def semantic_search(self, query: str, limit: int = 10, score_threshold: float = 0.5, filters: Optional[Dict] = None) -> List[Dict]:
        # Giữ nguyên code vector search của bạn vì nó khá ổn
        query_vector = self.embedding_service.get_embedding(query)
        results = qdrant_manager.search(
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            # Lưu ý: check lại bên qdrant_manager xem tham số là filter_conditions hay query_filter
        )
        
        return [{
            "id": r.id,
            "name": r.payload.get("name"),
            "brand": r.payload.get("brand"),
            "price": r.payload.get("price"),
            "image_path": r.payload.get("image_path"), # Đổi image thành image_path cho khớp database
            "similarity_score": round(r.score * 100, 2),
            "search_type": "semantic"
        } for r in results]

    def traditional_search(self, query: str, category_id: int = None, min_price: float = None, max_price: float = None) -> List[Dict]:
        """Đưa logic SQL cũ của bạn vào đây"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            sql = """
                SELECT id, name, brand, price, image_path, description, category_id, budget_id 
                FROM products 
                WHERE (name ILIKE %s OR description ILIKE %s OR brand ILIKE %s)
            """
            search_term = f"%{query}%"
            params = [search_term, search_term, search_term]

            if category_id:
                sql += " AND category_id = %s"
                params.append(category_id)
            if min_price:
                sql += " AND price >= %s"
                params.append(min_price)
            if max_price:
                sql += " AND price <= %s"
                params.append(max_price)

            cur.execute(sql, params)
            rows = cur.fetchall()
            return [{
                "id": r[0], "name": r[1], "brand": r[2], "price": r[3],
                "image_path": r[4], "description": r[5], "category_id": r[6], "budget_id": r[7], "search_type": "sql"
            } for r in rows]
        finally:
            cur.close()
            release_db_connection(conn)

# Khởi tạo instance duy nhất
search_service = SearchService()

# Giữ lại hàm này bên ngoài class để không làm hỏng main.py cũ
def get_all_categories():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name FROM categories ORDER BY name ASC;")
        return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]
    finally:
        cur.close()
        release_db_connection(conn)