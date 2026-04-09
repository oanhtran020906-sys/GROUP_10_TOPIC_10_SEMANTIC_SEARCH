from fastapi import FastAPI, Query
from typing import List, Optional
from services.sql_search import search_products_sql
from schema.product import ProductResponse

app = FastAPI(title="Product Semantic Search API")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
    '''
    How to test sql_search function
    when run main.py, ctrl click on http://127.0.0.1:8000, on web page, edit url to http://127.0.0.1:8000/docs (added /docs)
    click on /search/sql, click 'Try it out'. insert q = laptop (or any keywords) and 'Execute'.
    '''
    