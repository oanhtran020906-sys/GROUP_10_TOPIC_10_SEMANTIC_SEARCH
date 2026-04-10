"""
Insert dữ liệu vào Qdrant sử dụng Sentence-Transformers
Chạy trong môi trường Python sạch (không dùng Anaconda)
"""

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import time
import os

print("=" * 70)
print("🚀 KẾT NỐI QDRANT VÀ INSERT DỮ LIỆU VỚI SENTENCE-TRANSFORMERS")
print("=" * 70)

# ============================================
# 1. KIỂM TRA MÔI TRƯỜNG
# ============================================

print(f"\n📌 Python path: {os.sys.executable}")
print(f"📌 Working directory: {os.getcwd()}")

# ============================================
# 2. KHỞI TẠO EMBEDDING MODEL
# ============================================

print("\n📥 Đang tải Sentence-Transformers model...")
print("   (Lần đầu chạy sẽ tải model ~80MB)")

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vector_size = model.get_sentence_embedding_dimension()
    print(f"✅ Model loaded successfully!")
    print(f"   📐 Vector dimension: {vector_size}")
    print(f"   🏷️  Model name: all-MiniLM-L6-v2")
except Exception as e:
    print(f"❌ Lỗi khi tải model: {e}")
    print("   Hãy kiểm tra kết nối internet hoặc cài đặt lại sentence-transformers")
    exit(1)

# ============================================
# 3. KẾT NỐI QDRANT
# ============================================

print("\n💾 Đang kết nối Qdrant...")
try:
    client = QdrantClient(path="./qdrant_data")
    print("✅ Qdrant connected (local mode - data saved in ./qdrant_data)")
except Exception as e:
    print(f"❌ Lỗi kết nối Qdrant: {e}")
    exit(1)

# ============================================
# 4. TẠO COLLECTION
# ============================================

collection_name = "tech_products"

# Xóa collection cũ nếu có
if client.collection_exists(collection_name):
    print(f"\n🗑️ Xóa collection cũ: {collection_name}")
    client.delete_collection(collection_name)

# Tạo collection mới
print(f"\n📁 Tạo collection mới: {collection_name}")
try:
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )
    print("✅ Collection created!")
except Exception as e:
    print(f"❌ Lỗi tạo collection: {e}")
    exit(1)

# ============================================
# 5. ĐỌC DỮ LIỆU CSV
# ============================================

csv_path = 'data/products.csv'
print(f"\n📂 Đang đọc file CSV: {csv_path}")

if not os.path.exists(csv_path):
    print(f"❌ Không tìm thấy file: {csv_path}")
    print("   Hãy đảm bảo file products.csv nằm trong thư mục data/")
    exit(1)

try:
    df = pd.read_csv(csv_path, encoding='utf-8')
    df = df.fillna('')
    print(f"✅ Đã đọc {len(df)} sản phẩm")
    print(f"   📋 Các cột: {list(df.columns)}")
except Exception as e:
    print(f"❌ Lỗi đọc CSV: {e}")
    exit(1)

# ============================================
# 6. TẠO EMBEDDING VÀ INSERT
# ============================================

print("\n🔄 Đang tạo embedding và insert vào Qdrant...")
print("-" * 50)

batch_size = 50
total = len(df)
start_time = time.time()

for i in range(0, total, batch_size):
    batch_df = df.iloc[i:i+batch_size]
    
    # Chuẩn bị text cho embedding
    texts = []
    for _, row in batch_df.iterrows():
        brand = row['brand'] if row['brand'] else ''
        # Kết hợp name, brand, description để tạo embedding
        text = f"{row['name']}. {brand}. {row['description']}"
        texts.append(text)
    
    # Tạo embeddings
    print(f"   🔄 Batch {i//batch_size + 1}: Đang tạo embedding cho {len(texts)} sản phẩm...")
    embeddings = model.encode(texts, normalize_embeddings=True)
    
    # Tạo points
    points = []
    for j, (idx, row) in enumerate(batch_df.iterrows()):
        points.append(
            PointStruct(
                id=int(idx),
                vector=embeddings[j].tolist(),
                payload={
                    'name': row['name'],
                    'brand': row['brand'] if row['brand'] else '',
                    'price': int(row['price']),
                    'category_id': int(row['category_id']),
                    'budget_id': int(row['budget_id']),
                    'image_path': row['image_path'],
                    'description': row['description'][:500]  # Lưu 500 ký tự đầu
                }
            )
        )
    
    # Insert vào Qdrant
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    print(f"   ✅ Batch {i//batch_size + 1}: Đã insert {min(i+batch_size, total)}/{total} sản phẩm")

elapsed_time = time.time() - start_time

# ============================================
# 7. KIỂM TRA KẾT QUẢ
# ============================================

print("\n" + "=" * 70)
print("📊 KẾT QUẢ INSERT")
print("=" * 70)

collection_info = client.get_collection(collection_name)
print(f"📁 Collection name: {collection_name}")
print(f"📊 Số lượng sản phẩm đã insert: {collection_info.points_count}")
print(f"⏱️  Thời gian thực hiện: {elapsed_time:.2f} giây")
if total > 0:
    print(f"⚡ Tốc độ: {elapsed_time/total:.3f} giây/sản phẩm")

# ============================================
# 8. THỬ TÌM KIẾM
# ============================================

print("\n" + "=" * 70)
print("🔍 THỬ TÌM KIẾM (kiểm tra dữ liệu)")
print("=" * 70)

test_query = "điện thoại chụp ảnh đẹp giá rẻ"
print(f"\n📝 Query: '{test_query}'")

# Chuyển query thành vector
query_vector = model.encode([test_query], normalize_embeddings=True)[0]

# Tìm kiếm
search_results = client.search(
    collection_name=collection_name,
    query_vector=query_vector.tolist(),
    limit=5
)

print("\n📦 Top 5 kết quả tìm kiếm:")
print("-" * 50)
for i, result in enumerate(search_results, 1):
    print(f"{i}. {result.payload['name']}")
    print(f"   🏷️  Thương hiệu: {result.payload['brand']}")
    print(f"   💰 Giá: {result.payload['price']:,}đ")
    print(f"   📊 Độ tương đồng: {result.score * 100:.2f}%")
    print()

# ============================================
# 9. THÔNG TIN LƯU TRỮ
# ============================================

print("=" * 70)
print("✅ HOÀN TẤT!")
print("=" * 70)
print(f"\n💾 Dữ liệu được lưu tại: {os.path.abspath('./qdrant_data')}")
print(f"📁 Collection name: {collection_name}")
print(f"📊 Tổng số sản phẩm: {collection_info.points_count}")
print(f"🎯 Vector dimension: {vector_size}")
print("\n✨ Bạn có thể sử dụng dữ liệu này cho semantic search!")

# Lưu thông tin vào file
with open('qdrant_info.txt', 'w', encoding='utf-8') as f:
    f.write("QDRANT DATABASE INFO\n")
    f.write("=" * 50 + "\n")
    f.write(f"Collection name: {collection_name}\n")
    f.write(f"Number of products: {collection_info.points_count}\n")
    f.write(f"Vector dimension: {vector_size}\n")
    f.write(f"Storage path: {os.path.abspath('./qdrant_data')}\n")
    f.write(f"Embedding model: all-MiniLM-L6-v2\n")
    f.write(f"Distance metric: Cosine\n")

print("\n📄 Thông tin đã được lưu vào file: qdrant_info.txt")