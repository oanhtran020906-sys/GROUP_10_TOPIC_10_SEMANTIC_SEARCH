from fastapi import FastAPI, Query
from typing import List, Optional
from services.search_services import search_products_sql, get_all_categories
from schema.product import ProductResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Product Semantic Search API")

# 1. Xác định đường dẫn tuyệt đối đến folder ảnh
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "data", "images")
print('base:', BASE_DIR)
print('img:', IMAGE_DIR)

# 2. "Mở cửa" thư mục ảnh ra ngoài web
app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

# 3. (Mẹo) Tạo URL gốc để dùng ở nhiều nơi
BASE_URL = "http://127.0.0.1:8000"

@app.get("/search/sql", response_model=List[ProductResponse])
async def sql_search(
    q: str = Query(..., description="Từ khóa tìm kiếm"),
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    Tìm kiếm sản phẩm bằng SQL truyền thống (Sử dụng ILIKE)
    """
    results = search_products_sql(
        query=q, 
        category_id=category_id, 
        min_price=min_price, 
        max_price=max_price
    )

    print(f"🔍 [SQL Search] Keyword: '{q}' | Found: {len(results)} products")

    return results

@app.get("/categories")
async def get_categories():
    """Lấy danh sách danh mục để đổ vào thanh Filter trên Frontend"""
    return get_all_categories()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

    '''
    How to test sql_search function
    when run main.py, ctrl click on http://127.0.0.1:8000, on web page, edit url to http://127.0.0.1:8000/docs (added /docs)
    click on /search/sql, click 'Try it out'. insert q = laptop (or any keywords) and 'Execute'.
    '''
    