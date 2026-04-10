"""
Test tìm kiếm ngữ nghĩa - Đã sửa lỗi
"""

import sys
import os
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import time

print("=" * 70)
print("🔍 SEMANTIC SEARCH TEST")
print("=" * 70)

# 1. Load model
print("\n📥 Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"✅ Model loaded! Vector size: {model.get_sentence_embedding_dimension()}")

# 2. Kết nối Qdrant
print("\n💾 Connecting to Qdrant...")
client = QdrantClient(path="./qdrant_data")
collection_name = "tech_products"
print(f"✅ Connected! Collection: {collection_name}")

# 3. Kiểm tra dữ liệu
info = client.get_collection(collection_name)
print(f"📊 Products in database: {info.points_count}")

# 4. Các câu query test
test_queries = [
    "tôi muốn mua điện thoại chụp ảnh đẹp",
    "camera an ninh ngoài trời chống nước",
    "laptop gaming cấu hình mạnh",
    "tai nghe bluetooth không dây chống ồn",
    "đồng hồ thông minh theo dõi sức khỏe",
    "bàn phím cơ cho game thủ",
    "chuột máy tính không dây",
    "loa bluetooth di động pin lâu"
]

print("\n" + "=" * 70)
print("🔎 KẾT QUẢ TÌM KIẾM")
print("=" * 70)

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    print("-" * 50)
    
    # Tạo vector cho query
    query_vector = model.encode([query], normalize_embeddings=True)[0]
    
    # Tìm kiếm
    try:
        response = client.query_points(
            collection_name=collection_name,
            query=query_vector.tolist(),
            limit=3
        )
        results = response.points
    except:
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            limit=3
        )
    
    if results:
        for i, hit in enumerate(results, 1):
            score = hit.score * 100
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            print(f"   {i}. [{score:5.1f}%] {bar}")
            print(f"      📱 {hit.payload.get('name', 'N/A')[:55]}")
            print(f"      💰 {hit.payload.get('price', 0):,}đ | 🏷️ {hit.payload.get('brand', 'N/A')}")
    else:
        print("   ❌ Không tìm thấy kết quả")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE!")
input("\nNhấn Enter để thoát...")