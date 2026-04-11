from fastapi import FastAPI, Query
from typing import List, Optional
from services.search_services import search_service # Import instance mới
from schema.product import ProductResponse
from fastapi.staticfiles import StaticFiles
from config import settings
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Product Semantic Search API")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả các nguồn, hoặc chỉ định rõ ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "data", "images")

app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

BASE_URL = "http://127.0.0.1:8000"

#lấy sản phẩm nổi bật
@app.get("/products", response_model=List[ProductResponse])
async def get_bestseller(
    limit: int = Query(4, ge=1, le=50),
    category_id: Optional[int] = None
):
    """Lấy danh sách sản phẩm (dùng cho trang chủ hoặc lọc nhanh)"""
    return search_service.get_bestseller(limit=limit, category_id=category_id)

#lấy product's detail khi mà nhấn vào sản phẩm
@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_detail(product_id: int):
    """Lấy thông tin chi tiết của 1 sản phẩm theo ID"""
    product = search_service.get_product_by_id(product_id)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return product

#endpoint cho search = sql
@app.get("/search/sql", response_model=List[ProductResponse])
async def sql_search(
    q: str = Query(..., description="Từ khóa tìm kiếm"),
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    results = search_service.traditional_search(
        query=q, 
        category_id=category_id, 
        min_price=min_price, 
        max_price=max_price
    )
    print(f"🔍 [SQL Search] Keyword: '{q}' | Found: {len(results)} products")
    return results


#Endpoint cho search = vector
@app.get("/search/vector", response_model=List[ProductResponse])
async def vector_search(q: str = Query(..., description="Tìm kiếm ý nghĩa")):
    results = search_service.semantic_search(query=q)
    print(f"🔍 [Vector Search] Keyword: '{q}' | Found: {len(results)} products")
    return results

#Lấy danh sách danh mục để đổ vào thanh Filter trên Frontend
@app.get("/categories")
async def get_categories():
    return search_service.get_all_categories()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

    '''
    How to test sql_search function
    when run main.py, ctrl click on http://127.0.0.1:8000, on web page, edit url to http://127.0.0.1:8000/docs (added /docs)
    click on /search/sql, click 'Try it out'. insert q = laptop (or any keywords) and 'Execute'.
    '''
    