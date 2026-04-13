from typing import List, Dict, Optional, Any
import logging
import re

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


    def traditional_search(self, query: str, limit: int = 4, category_id: int = None, min_price: float = None, max_price: float = None) -> List[Dict]:
        """Đưa logic SQL cũ của bạn vào đây"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            sql = """
                SELECT id, name, brand, price, image_path, description, category_id, budget_id 
                FROM products 
                WHERE (name ILIKE %s OR description ILIKE %s OR brand ILIKE %s)
                LIMIT %s
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

    def _internal_token_search(self, tokens: List[str], limit: int) -> List[Dict]:
        """Hàm bổ trợ tìm kiếm sản phẩm chứa các tokens (Chỉ dùng nội bộ cho Hybrid)"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            token_conditions = []
            params = []
            for t in tokens:
                token_conditions.append("(name ILIKE %s OR brand ILIKE %s)")
                term = f"%{t}%"
                params.extend([term, term])
                
            sql = f"""
                SELECT id, name, brand, price, image_path, description, category_id, budget_id 
                FROM products 
                WHERE {" OR ".join(token_conditions)}
                LIMIT %s
            """
            params.append(limit)
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [{
                "id": r[0], "name": r[1], "brand": r[2], "price": r[3],
                "image_path": r[4], "description": r[5], "category_id": r[6], "budget_id": r[7]
            } for r in rows]
        finally:
            cur.close()
            release_db_connection(conn)

    def hybrid_search(
        self,
        query: str,
        limit: int = 4,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict]:
        """
        Hybrid search: Kết hợp Semantic (AI) và Keyword (Tokenized SQL)
        """
        search_limit = limit * 3 # Lấy rộng hơn để re-rank cho chuẩn
        
        # 1. Lấy kết quả Semantic (AI)
        semantic_results = self.semantic_search(query, limit=search_limit)
        
        # 2. Lấy kết quả Keyword dựa trên Tokenization (Chỉ dùng cho Hybrid)
        # Tách từ và lọc bỏ từ thừa
        clean_query = re.sub(r'[^\w\s]', '', query).lower()
        stop_words = {"cho", "tôi", "muốn", "tìm", "cái", "mình", "là", "và", "có", "một", "những"}
        tokens = [t for t in clean_query.split() if t not in stop_words and len(t) > 1]
        
        keyword_results = []
        if tokens:
            # Gọi logic tìm kiếm theo tokens (Bạn có thể viết một hàm riêng hoặc thực thi SQL tại đây)
            keyword_results = self._internal_token_search(tokens, limit=search_limit)
        else:
            # Nếu không tách được token, dùng search truyền thống làm backup
            keyword_results = self.traditional_search(query, limit=search_limit)
        
        combined = {}

        # 3. Trộn kết quả Semantic
        for result in semantic_results:
            p_id = result["id"]
            score = result.get("similarity_score", 0)
            # Chuẩn hóa score về 0-1 nếu Qdrant trả về 0-100
            normalized_score = score / 100 if score > 1 else score
            
            # Tạo object mới để không ảnh hưởng đến dữ liệu gốc của semantic_search
            new_result = result.copy()
            new_result["combined_score"] = normalized_score * semantic_weight
            new_result["search_type"] = "hybrid" # Chốt search_type là hybrid
            new_result["is_keyword_match"] = False
            combined[p_id] = new_result

        # 4. Trộn kết quả Keyword (Tokenized)
        for result in keyword_results:
            p_id = result["id"]
            # Thưởng điểm cho việc khớp từ khóa
            bonus_score = 1.0 * keyword_weight
            
            if p_id in combined:
                combined[p_id]["combined_score"] += bonus_score
                combined[p_id]["is_keyword_match"] = True
            else:
                new_result = result.copy()
                new_result["combined_score"] = bonus_score
                new_result["search_type"] = "hybrid"
                new_result["is_keyword_match"] = True
                combined[p_id] = new_result

        # 5. Sắp xếp và trả về top kết quả
        sorted_results = sorted(
            combined.values(), 
            key=lambda x: x["combined_score"], 
            reverse=True
        )
        
        return sorted_results[:limit]

    def get_bestseller(self, limit: int = 8, category_id: Optional[int] = None) -> List[Dict]:
        """Lấy sản phẩm ngẫu nhiên từ PostgreSQL để làm sản phẩm nổi bật"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # RANDOM() trong PostgreSQL giúp lấy dữ liệu ngẫu nhiên mỗi lần load trang
            sql = "SELECT id, name, brand, price, image_path, description, category_id, budget_id FROM products"
            params = []

            if category_id:
                sql += " WHERE category_id = %s"
                params.append(category_id)
            
            sql += " ORDER BY RANDOM() LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)
            rows = cur.fetchall()
            
            return [{
                "id": r[0], "name": r[1], "brand": r[2], "price": r[3],
                "image_path": r[4], "description": r[5], 
                "category_id": r[6], "budget_id": r[7], 
                "search_type": "sql" # Đánh dấu để frontend biết đây là dữ liệu gốc
            } for r in rows]
        finally:
            cur.close()
            release_db_connection(conn)

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Lấy thông tin chi tiết của một sản phẩm dựa trên ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            sql = "SELECT id, name, brand, price, image_path, description, category_id, budget_id FROM products WHERE id = %s"
            cur.execute(sql, (product_id,))
            r = cur.fetchone()
            
            if not r:
                return None
                
            return {
                "id": r[0], "name": r[1], "brand": r[2], "price": r[3],
                "image_path": r[4], "description": r[5], 
                "category_id": r[6], "budget_id": r[7],
                "search_type": "sql"
            }
        finally:
            cur.close()
            release_db_connection(conn)

    def get_all_categories():
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, name FROM categories ORDER BY name ASC;")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]
        finally:
            cur.close()
            release_db_connection(conn)

# Khởi tạo instance duy nhất
search_service = SearchService()

