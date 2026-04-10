"""
Tech Store Semantic Search - Main Application
FastAPI backend with Qdrant vector database
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List, Dict, Any
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tech Store Semantic Search",
    description="Tìm kiếm sản phẩm bằng ngữ nghĩa với Qdrant + Sentence-Transformers",
    version="1.0.0"
)

# CORS middleware - Cho phép frontend React kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# KHỞI TẠO SEMANTIC SEARCH SERVICE
# ============================================

model = None
client = None
collection_name = "tech_products"

# Lấy đường dẫn gốc
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init_search_service():
    """Khởi tạo semantic search service"""
    global model, client
    
    try:
        from sentence_transformers import SentenceTransformer
        from qdrant_client import QdrantClient
        
        # Load model
        logger.info("📥 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(f"✅ Model loaded! Vector size: {model.get_sentence_embedding_dimension()}")
        
        # Connect to Qdrant
        logger.info("🔌 Connecting to Qdrant...")
        client = QdrantClient(host="localhost", port=6333, check_compatibility=False)
        client.get_collections()
        logger.info("✅ Connected to Qdrant Server")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        return False


def semantic_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Thực hiện tìm kiếm ngữ nghĩa"""
    global model, client, collection_name
    
    if model is None or client is None:
        return []
    
    try:
        # Tạo vector cho query
        query_vector = model.encode([query], normalize_embeddings=True)[0]
        
        # Tìm kiếm trong Qdrant
        try:
            response = client.query_points(
                collection_name=collection_name,
                query=query_vector.tolist(),
                limit=limit,
                score_threshold=0.3
            )
            results = response.points
        except AttributeError:
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                score_threshold=0.3
            )
        
        # Format kết quả
        return [
            {
                "id": hit.id,
                "name": hit.payload.get("name", "N/A"),
                "brand": hit.payload.get("brand", ""),
                "price": hit.payload.get("price", 0),
                "category_id": hit.payload.get("category_id", 0),
                "budget_id": hit.payload.get("budget_id", 0),
                "image_path": hit.payload.get("image_path", ""),
                "similarity_score": round(hit.score * 100, 2),
                "description": hit.payload.get("description", "")[:200]
            }
            for hit in results
        ]
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []


def get_csv_path():
    """Tìm đường dẫn đến file CSV"""
    possible_paths = [
        os.path.join(BASE_DIR, "backend", "data", "raw", "products.csv"),
        os.path.join(BASE_DIR, "data", "raw", "products.csv"),
        os.path.join(os.path.dirname(__file__), "data", "raw", "products.csv"),
        "data/raw/products.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


# ============================================
# API ENDPOINTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Khởi tạo service khi app start"""
    print("\n" + "=" * 50)
    print("🚀 STARTING TECH STORE SEMANTIC SEARCH API")
    print("=" * 50)
    
    success = init_search_service()
    
    if success:
        try:
            info = client.get_collection(collection_name)
            print(f"✅ Semantic search service ready!")
            print(f"📁 Collection: {collection_name}")
            print(f"📊 Products indexed: {info.points_count}")
        except:
            print(f"✅ Semantic search service ready!")
            print(f"📁 Collection: {collection_name}")
        
        print(f"\n🌐 API Endpoints:")
        print(f"   GET  http://localhost:8000/health")
        print(f"   GET  http://localhost:8000/api/search?q=...")
        print(f"   GET  http://localhost:8000/api/sql-search?q=...")
        print(f"   GET  http://localhost:8000/api/compare?q=...")
        print(f"   GET  http://localhost:8000/api/products")
    else:
        print("❌ Failed to initialize semantic search service")
        print("   Make sure Qdrant server is running: qdrant.exe")
    
    print("=" * 50)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global model, client, collection_name
    
    if model is None or client is None:
        return {
            "status": "error", 
            "message": "Semantic search service not initialized",
            "service": "semantic-search"
        }
    
    try:
        info = client.get_collection(collection_name)
        return {
            "status": "healthy",
            "service": "semantic-search",
            "collection": collection_name,
            "indexed_products": info.points_count,
            "embedding_model": "all-MiniLM-L6-v2",
            "vector_size": 384
        }
    except Exception as e:
        return {
            "status": "degraded", 
            "message": str(e),
            "service": "semantic-search"
        }


@app.get("/api/search")
async def api_semantic_search(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Semantic search endpoint using vector similarity
    """
    results = semantic_search(q, limit)
    return {
        "query": q,
        "results": results,
        "total": len(results),
        "type": "semantic"
    }


@app.get("/api/sql-search")
async def api_sql_search(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Traditional SQL LIKE search for comparison
    """
    try:
        csv_path = get_csv_path()
        
        if csv_path is None:
            return {
                "query": q,
                "results": [],
                "total": 0,
                "type": "sql",
                "error": "CSV file not found"
            }
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        df = df.fillna('')
        
        query_lower = q.lower()
        results = []
        
        for idx, row in df.iterrows():
            search_text = f"{row['name']} {row['brand']} {row['description']}".lower()
            if query_lower in search_text:
                results.append({
                    "id": idx,
                    "name": row['name'],
                    "brand": row['brand'] if row['brand'] else '',
                    "price": int(row['price']),
                    "similarity_score": 100
                })
        
        return {
            "query": q,
            "results": results[:limit],
            "total": len(results[:limit]),
            "type": "sql"
        }
    except Exception as e:
        return {
            "query": q,
            "results": [],
            "total": 0,
            "type": "sql",
            "error": str(e)
        }


@app.get("/api/compare")
async def api_compare_search(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Compare semantic search vs SQL search side by side
    """
    # Semantic search results
    semantic_results = semantic_search(q, limit)
    
    # SQL search results
    try:
        csv_path = get_csv_path()
        
        if csv_path is None:
            return {
                "query": q,
                "semantic": semantic_results,
                "sql": [],
                "semantic_count": len(semantic_results),
                "sql_count": 0,
                "error": "CSV file not found"
            }
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        df = df.fillna('')
        
        query_lower = q.lower()
        sql_results = []
        
        for idx, row in df.iterrows():
            search_text = f"{row['name']} {row['brand']} {row['description']}".lower()
            if query_lower in search_text:
                sql_results.append({
                    "id": idx,
                    "name": row['name'],
                    "brand": row['brand'] if row['brand'] else '',
                    "price": int(row['price'])
                })
        
        return {
            "query": q,
            "semantic": semantic_results,
            "sql": sql_results[:limit],
            "semantic_count": len(semantic_results),
            "sql_count": len(sql_results[:limit])
        }
    except Exception as e:
        return {
            "query": q,
            "semantic": semantic_results,
            "sql": [],
            "semantic_count": len(semantic_results),
            "sql_count": 0,
            "error": str(e)
        }


@app.get("/api/products")
async def api_get_products(
    limit: int = Query(50, ge=1, le=200, description="Number of products"),
    skip: int = Query(0, ge=0, description="Skip count"),
    category_id: int = Query(None, description="Filter by category")
):
    """
    Get all products with pagination and filtering
    """
    try:
        csv_path = get_csv_path()
        
        if csv_path is None:
            return {
                "products": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "error": "CSV file not found"
            }
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        df = df.fillna('')
        
        # Filter by category if provided
        if category_id:
            df = df[df['category_id'] == category_id]
        
        total = len(df)
        df = df.iloc[skip:skip+limit]
        
        products = []
        for idx, row in df.iterrows():
            products.append({
                "id": int(idx),
                "name": row['name'],
                "brand": row['brand'] if row['brand'] else '',
                "price": int(row['price']),
                "category_id": int(row['category_id']),
                "budget_id": int(row['budget_id']),
                "image_path": row['image_path'],
                "description": row['description'][:200] + "..." if len(row['description']) > 200 else row['description']
            })
        
        return {
            "products": products,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        return {
            "products": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "error": str(e)
        }


@app.get("/api/categories")
async def api_get_categories():
    """
    Get all categories with product counts
    """
    try:
        csv_path = get_csv_path()
        
        if csv_path is None:
            return {"categories": []}
        
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        categories = {
            1: "Camera an ninh",
            2: "Điện thoại",
            3: "Đồng hồ thông minh",
            4: "Máy tính bảng",
            5: "Bàn phím",
            6: "Màn hình",
            7: "Tai nghe",
            8: "Laptop",
            9: "Chuột",
            10: "Loa"
        }
        
        result = []
        for cat_id, cat_name in categories.items():
            count = len(df[df['category_id'] == cat_id])
            if count > 0:
                result.append({
                    "id": cat_id,
                    "name": cat_name,
                    "product_count": int(count)
                })
        
        return {"categories": result}
    except Exception as e:
        return {"categories": [], "error": str(e)}


@app.get("/api/stats")
async def api_get_stats():
    """
    Get system statistics
    """
    stats = {
        "service": "semantic-search",
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_size": 384,
        "collection_name": collection_name
    }
    
    # Get Qdrant stats
    if client is not None:
        try:
            info = client.get_collection(collection_name)
            stats["indexed_products"] = info.points_count
        except:
            stats["indexed_products"] = 0
    else:
        stats["indexed_products"] = 0
    
    # Get CSV stats
    try:
        csv_path = get_csv_path()
        if csv_path:
            df = pd.read_csv(csv_path, encoding='utf-8')
            stats["total_products_in_csv"] = len(df)
    except:
        stats["total_products_in_csv"] = 0
    
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )