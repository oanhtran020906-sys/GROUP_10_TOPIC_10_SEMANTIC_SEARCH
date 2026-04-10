"""
Insert sản phẩm vào Qdrant SERVER (có UI)
QUAN TRỌNG: Phải kết nối đến server đang chạy, không phải local mode
"""

import sys
import os

# Thêm đường dẫn
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import time
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

print("=" * 60)
print("📦 INSERTING PRODUCTS TO QDRANT SERVER")
print("=" * 60)

# ============================================
# 1. KẾT NỐI ĐẾN QDRANT SERVER (QUAN TRỌNG)
# ============================================
# Phải dùng host và port, không dùng path
try:
    client = QdrantClient(host="localhost", port=6333)
    # Kiểm tra kết nối
    client.get_collections()
    print("✅ Connected to Qdrant Server at localhost:6333")
    print("   🌐 UI: http://localhost:6333/dashboard")
except Exception as e:
    print(f"❌ Cannot connect to Qdrant Server: {e}")
    print("\n💡 Please start Qdrant server first:")
    print("   cd D:\\qdrant && qdrant.exe")
    sys.exit(1)

# ============================================
# 2. CẤU HÌNH
# ============================================
collection_name = "tech_products"  # Tên collection muốn tạo
csv_path = "data/raw/products.csv"  # Đường dẫn file CSV

# ============================================
# 3. LOAD MODEL
# ============================================
print("\n📥 Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
vector_size = model.get_sentence_embedding_dimension()
print(f"✅ Model loaded! Vector size: {vector_size}")

# ============================================
# 4. ĐỌC CSV
# ============================================
print(f"\n📂 Reading CSV: {csv_path}")

if not os.path.exists(csv_path):
    print(f"❌ File not found: {csv_path}")
    sys.exit(1)

df = pd.read_csv(csv_path, encoding='utf-8')
df = df.fillna('')
print(f"✅ Loaded {len(df)} products")

# ============================================
# 5. XÓA COLLECTION CŨ NẾU CÓ
# ============================================
if client.collection_exists(collection_name):
    print(f"\n🗑️ Deleting existing collection: {collection_name}")
    client.delete_collection(collection_name)
    print("   ✅ Deleted")

# ============================================
# 6. TẠO COLLECTION MỚI
# ============================================
print(f"\n📁 Creating collection: {collection_name}")
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=vector_size,
        distance=Distance.COSINE
    )
)
print(f"✅ Collection '{collection_name}' created!")

# ============================================
# 7. TẠO TEXT CHO EMBEDDING
# ============================================
print("\n🔄 Preparing texts for embedding...")
texts = []
for _, row in df.iterrows():
    brand = row['brand'] if row['brand'] else ''
    text = f"{row['name']}. {brand}. {row['description']}"
    texts.append(text)

# ============================================
# 8. TẠO EMBEDDINGS
# ============================================
print(f"\n🔄 Generating embeddings for {len(texts)} products...")

start_time = time.time()
batch_size = 50
all_embeddings = []

for i in range(0, len(texts), batch_size):
    batch_texts = texts[i:i+batch_size]
    batch_embeddings = model.encode(batch_texts, normalize_embeddings=True)
    all_embeddings.append(batch_embeddings)
    print(f"   ✅ Processed {min(i+batch_size, len(texts))}/{len(texts)}")

embeddings = np.vstack(all_embeddings)
elapsed = time.time() - start_time
print(f"✅ Embeddings generated in {elapsed:.2f}s")
print(f"   Shape: {embeddings.shape}")

# ============================================
# 9. INSERT VÀO QDRANT
# ============================================
print(f"\n🔄 Inserting into Qdrant...")

points = []
for idx, row in df.iterrows():
    point = PointStruct(
        id=int(idx),
        vector=embeddings[idx].tolist(),
        payload={
            'name': str(row['name']),
            'brand': str(row['brand']) if row['brand'] else '',
            'price': int(row['price']),
            'category_id': int(row['category_id']),
            'budget_id': int(row['budget_id']),
            'image_path': str(row['image_path']),
            'description': str(row['description'])[:500]
        }
    )
    points.append(point)

start_time = time.time()
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    client.upsert(collection_name=collection_name, points=batch)
    print(f"   ✅ Inserted {min(i+batch_size, len(points))}/{len(points)}")

elapsed = time.time() - start_time

# ============================================
# 10. KIỂM TRA KẾT QUẢ
# ============================================
collection_info = client.get_collection(collection_name)

print("\n" + "=" * 60)
print("✅ INSERT COMPLETE!")
print("=" * 60)
print(f"📁 Collection: {collection_name}")
print(f"📊 Products indexed: {collection_info.points_count}")
print(f"⏱️ Time: {elapsed:.2f} seconds")

print("\n🌐 REFRESH your browser at: http://localhost:6333/dashboard")
print(f"   You will see collection '{collection_name}' next to 'laptop_products'")