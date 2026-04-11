from typing import List, Dict, Optional, Any
import logging
from database.postgres import get_db_connection, release_db_connection
from services.embedding_service import embedding_service
from database.qdrant import qdrant_store


logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.embedding_service = embedding_service

    def semantic_search(self, query: str, limit: int = 5, score_threshold: float = 0.1, filters: Optional[Dict] = None) -> List[Dict]:
        query_vector = self.embedding_service.get_embedding(query)
        
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()

        results = qdrant_store.semantic_search(
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
            # Nếu bạn có truyền thêm category_filter, min_price... thì thêm vào đây
        )
        
        formatted_response = []
        for r in results:
            formatted_response.append({
                "id": r.get("product_id"),         # FastAPI đòi 'id', ta lấy từ 'product_id'
                "name": r.get("name"),
                "description": r.get("description"),
                "price": r.get("price"),
                "brand": r.get("brand", "Unknown"), # Nếu thiếu brand thì để mặc định
                "category_id": r.get("category_id", 0), # Nếu thiếu category_id thì để 0
                "budget_id": r.get("budget_id"),
                "image_path": r.get("image_url") or r.get("image_path"),
                "similarity_score": r.get("similarity_score"),
                "search_type": "semantic"
            })
        
        return formatted_response


    def traditional_search(self, query: str, limit: int = 5, category_id: int = None, min_price: float = None, max_price: float = None) -> List[Dict]:
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

            sql += " LIMIT %s"
            params.append(limit) # Sử dụng biến limit truyền vào hàm (mặc định là 5)

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