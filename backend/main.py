from fastapi import FastAPI, Query
from typing import List, Optional
from services.search_services import search_service, get_all_categories # Import instance mới
from schema.product import ProductResponse
from fastapi.staticfiles import StaticFiles
from config import settings
import os

app = FastAPI(title="Product Semantic Search API")


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
    # Gọi thông qua search_service
    results = search_service.traditional_search(
        query=q, 
        category_id=category_id, 
        min_price=min_price, 
        max_price=max_price
    )
    print(f"🔍 [SQL Search] Keyword: '{q}' | Found: {len(results)} products")
    return results

@app.get("/search/vector", response_model=List[ProductResponse])
async def vector_search(q: str = Query(..., description="Tìm kiếm ý nghĩa")):
    """Endpoint mới cho chế độ VECTOR (màu tím)"""
    results = search_service.semantic_search(query=q)
    print(f"🔍 [Vector Search] Keyword: '{q}' | Found: {len(results)} products")
    return results

@app.get("/categories")
async def get_categories():
    """Lấy danh sách danh mục để đổ vào thanh Filter trên Frontend"""
    return get_all_categories()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

    '''
    How to test sql_search function
    when run main.py, ctrl click on http://127.0.0.1:8000, on web page, edit url to http://127.0.0.1:8000/docs (added /docs)
    click on /search/sql, click 'Try it out'. insert q = laptop (or any keywords) and 'Execute'.
    '''
    