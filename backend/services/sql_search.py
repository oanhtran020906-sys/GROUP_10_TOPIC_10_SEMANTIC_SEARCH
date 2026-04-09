 # SQL search
from database.postgres import get_db_connection, release_db_connection

def search_products_sql(query: str, category_id: int = None, min_price: float = None, max_price: float = None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Câu lệnh SQL cơ bản với ILIKE (không phân biệt hoa thường)
        sql = """
            SELECT id, name, brand, price, image_path, description, category_id, budget_id 
            FROM products 
            WHERE (name ILIKE %s OR description ILIKE %s OR brand ILIKE %s)
        """
        # %query% giúp tìm kiếm từ khóa ở bất kỳ vị trí nào trong chuỗi
        search_term = f"%{query}%"
        params = [search_term, search_term, search_term]

        # Thêm các bộ lọc nếu có
        if category_id:
            sql += " AND category_id = %s"
            params.append(category_id)
        
        if min_price is not None:
            sql += " AND price >= %s"
            params.append(min_price)
            
        if max_price is not None:
            sql += " AND price <= %s"
            params.append(max_price)

        cur.execute(sql, params)
        rows = cur.fetchall()
        
        # Chuyển đổi kết quả từ tuple sang list các dictionary
        products = []
        for row in rows:
            products.append({
                "id": row[0], "name": row[1], "brand": row[2],
                "price": row[3], "image_path": row[4], "description": row[5],
                "category_id": row[6], "budget_id": row[7]
            })
        return products

    finally:
        cur.close()
        release_db_connection(conn)