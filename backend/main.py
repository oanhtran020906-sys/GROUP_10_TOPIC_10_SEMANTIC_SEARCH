"""
Tech Store Semantic Search - Main Application
FastAPI backend with Qdrant vector database
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tech Store Semantic Search",
    description="Tìm kiếm sản phẩm bằng ngữ nghĩa với Qdrant + Sentence-Transformers",
    version="1.0.0"
)

# CORS middleware
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

# Global variables
search_service = None
model = None
client = None
collection_name = "tech_products"


def init_search_service():
    """Khởi tạo semantic search service"""
    global search_service, model, client
    
    try:
        from sentence_transformers import SentenceTransformer
        from qdrant_client import QdrantClient
        
        # Load model
        logger.info("📥 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(f"✅ Model loaded! Vector size: {model.get_sentence_embedding_dimension()}")
        
        # Connect to Qdrant
        logger.info("🔌 Connecting to Qdrant...")
        client = QdrantClient(host="localhost", port=6333)
        client.get_collections()  # Test connection
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
        print(f"✅ Semantic search service ready!")
        print(f"📁 Collection: {collection_name}")
        print(f"\n🌐 API endpoints:")
        print(f"   GET  /              - Web UI")
        print(f"   GET  /health        - Health check")
        print(f"   GET  /api/search    - Semantic search")
        print(f"   GET  /api/sql-search - SQL LIKE search")
        print(f"   GET  /api/compare   - Compare both")
    else:
        print("❌ Failed to initialize semantic search service")
        print("   Make sure Qdrant server is running: qdrant.exe")
    
    print("=" * 50)


@app.get("/")
async def root():
    """Web UI cho semantic search"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔍 Tech Store - Semantic Search</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { text-align: center; color: white; margin-bottom: 10px; font-size: 2.5rem; }
            .subtitle { text-align: center; color: rgba(255,255,255,0.9); margin-bottom: 30px; }
            .search-box {
                background: white;
                border-radius: 60px;
                padding: 5px;
                display: flex;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .search-box input {
                flex: 1;
                padding: 18px 25px;
                font-size: 16px;
                border: none;
                background: transparent;
                outline: none;
            }
            .search-box button {
                padding: 15px 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
            }
            .comparison {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .column {
                background: white;
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .column h2 {
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }
            .product-card {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                transition: all 0.2s;
            }
            .product-card:hover {
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102,126,234,0.15);
            }
            .product-name { font-weight: 600; font-size: 16px; color: #333; }
            .product-brand { color: #666; font-size: 13px; margin: 5px 0; }
            .product-price { color: #ff6b6b; font-weight: bold; }
            .similarity {
                display: inline-block;
                background: #4caf50;
                color: white;
                padding: 2px 10px;
                border-radius: 20px;
                font-size: 11px;
                margin-top: 8px;
            }
            .loading { text-align: center; padding: 40px; color: #999; }
            .example-queries {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
                margin-bottom: 30px;
            }
            .example-chip {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 13px;
                cursor: pointer;
            }
            @media (max-width: 768px) {
                .comparison { grid-template-columns: 1fr; }
                h1 { font-size: 1.8rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Tech Store - Semantic Search</h1>
            <p class="subtitle">Tìm kiếm bằng ngữ nghĩa - Hiểu đúng ý bạn, không cần từ khóa chính xác</p>
            
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Ví dụ: tôi muốn mua điện thoại chụp ảnh đẹp giá dưới 15 triệu">
                <button onclick="search()">🔍 Tìm kiếm</button>
            </div>
            
            <div class="example-queries" id="exampleQueries"></div>
            
            <div class="comparison">
                <div class="column">
                    <h2>🎯 Vector Search (Ngữ nghĩa)</h2>
                    <div id="semanticResults">💡 Nhập nội dung tìm kiếm ở trên</div>
                </div>
                <div class="column">
                    <h2>📝 SQL LIKE Search (Từ khóa)</h2>
                    <div id="sqlResults">💡 Nhập nội dung tìm kiếm ở trên</div>
                </div>
            </div>
        </div>
        
        <script>
            const examples = [
                "tôi muốn mua điện thoại chụp ảnh đẹp",
                "camera an ninh ngoài trời chống nước",
                "laptop gaming cấu hình mạnh",
                "tai nghe bluetooth không dây"
            ];
            
            const container = document.getElementById('exampleQueries');
            examples.forEach(query => {
                const chip = document.createElement('div');
                chip.className = 'example-chip';
                chip.textContent = query;
                chip.onclick = () => {
                    document.getElementById('searchInput').value = query;
                    search();
                };
                container.appendChild(chip);
            });
            
            async function search() {
                const query = document.getElementById('searchInput').value;
                if (!query.trim()) return;
                
                document.getElementById('semanticResults').innerHTML = '<div class="loading">⏳ Đang tìm kiếm...</div>';
                document.getElementById('sqlResults').innerHTML = '<div class="loading">⏳ Đang tìm kiếm...</div>';
                
                try {
                    const response = await fetch(`/api/compare?q=${encodeURIComponent(query)}&limit=8`);
                    const data = await response.json();
                    
                    // Semantic results
                    if (data.semantic && data.semantic.length > 0) {
                        document.getElementById('semanticResults').innerHTML = data.semantic.map(r => `
                            <div class="product-card">
                                <div class="product-name">${r.name}</div>
                                <div class="product-brand">🏷️ ${r.brand || 'Thương hiệu nổi bật'}</div>
                                <div class="product-price">💰 ${r.price.toLocaleString()}đ</div>
                                <div class="similarity">🎯 Độ tương đồng: ${r.similarity_score}%</div>
                            </div>
                        `).join('');
                    } else {
                        document.getElementById('semanticResults').innerHTML = '<div class="loading">❌ Không tìm thấy kết quả</div>';
                    }
                    
                    // SQL results
                    if (data.sql && data.sql.length > 0) {
                        document.getElementById('sqlResults').innerHTML = data.sql.map(r => `
                            <div class="product-card">
                                <div class="product-name">${r.name}</div>
                                <div class="product-brand">🏷️ ${r.brand || 'Thương hiệu nổi bật'}</div>
                                <div class="product-price">💰 ${r.price.toLocaleString()}đ</div>
                            </div>
                        `).join('');
                    } else {
                        document.getElementById('sqlResults').innerHTML = '<div class="loading">❌ SQL không tìm thấy (vì từ khóa không khớp chính xác)</div>';
                    }
                } catch (error) {
                    document.getElementById('semanticResults').innerHTML = '<div class="loading">⚠️ Lỗi kết nối</div>';
                    document.getElementById('sqlResults').innerHTML = '<div class="loading">⚠️ Lỗi kết nối</div>';
                }
            }
            
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') search();
            });
        </script>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global model, client, collection_name
    
    if model is None or client is None:
        return {"status": "error", "message": "Semantic search service not initialized"}
    
    try:
        info = client.get_collection(collection_name)
        return {
            "status": "healthy",
            "service": "semantic-search",
            "collection": collection_name,
            "indexed_products": info.points_count,
            "embedding_model": "all-MiniLM-L6-v2"
        }
    except Exception as e:
        return {"status": "degraded", "message": str(e)}


@app.get("/api/search")
async def search_semantic(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Semantic search endpoint"""
    results = semantic_search(q, limit)
    return {
        "query": q,
        "results": results,
        "total": len(results),
        "type": "semantic"
    }


@app.get("/api/sql-search")
async def search_sql(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """SQL LIKE search for comparison"""
    import pandas as pd
    
    try:
        df = pd.read_csv("data/raw/products.csv", encoding='utf-8')
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
        return {"query": q, "results": [], "total": 0, "error": str(e)}


@app.get("/api/compare")
async def compare_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Compare semantic search vs SQL search"""
    semantic_results = semantic_search(q, limit)
    
    import pandas as pd
    df = pd.read_csv("data/raw/products.csv", encoding='utf-8')
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )