# run_insert.py - Đặt ở thư mục GỐC
import sys
import os
import pandas as pd
import time

# Thêm backend vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.qdrant import init_qdrant
from services.embedding_service import embedding_service
from qdrant_client.models import PointStruct

# Import config từ thư mục gốc
from config import settings

print("=" * 60)
print("🚀 PRODUCT EMBEDDING & INSERTION SCRIPT")
print("=" * 60)

# Check API key
if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
    print("❌ Please set your OpenAI API key in .env file")
    exit(1)

# Initialize Qdrant
manager = init_qdrant(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    collection_name=settings.QDRANT_COLLECTION_NAME
)

# Delete old collection
if manager.collection_exists():
    print("Deleting existing collection...")
    manager.delete_collection()
    time.sleep(1)

# Create new collection
manager.create_collection(vector_size=settings.TEXT_EMBEDDING_DIMENSION)

# Load CSV
csv_path = "backend/data/raw/products.csv"
if not os.path.exists(csv_path):
    csv_path = "products.csv"

if not os.path.exists(csv_path):
    print(f"❌ CSV file not found: {csv_path}")
    exit(1)

print(f"Found CSV at: {csv_path}")
df = pd.read_csv(csv_path)
df.columns = df.columns.str.replace('\ufeff', '')

category_map = {
    1: "Camera", 2: "Điện thoại", 3: "Smartwatch", 4: "Tablet",
    5: "Bàn phím", 6: "Màn hình", 7: "Tai nghe", 8: "Laptop",
    9: "Chuột", 10: "Loa"
}

products = []
for idx, row in df.iterrows():
    try:
        price = float(str(row.get('price', '0')).replace(',', ''))
    except:
        price = 0
    
    product = {
        "id": idx + 1,
        "name": str(row.get('name', '')),
        "brand": str(row.get('brand', '')) if pd.notna(row.get('brand')) else "Unknown",
        "price": price,
        "description": str(row.get('description', '')),
        "category_id": int(row.get('category_id', 0)) if pd.notna(row.get('category_id')) else 0,
    }
    product["category"] = category_map.get(product["category_id"], "Other")
    
    if product['name'] and product['name'] != 'nan':
        products.append(product)

print(f"\n📊 Total products: {len(products)}")

# Generate embeddings
print(f"\n🔄 Generating embeddings using OpenAI...")
points = []

for i, product in enumerate(products):
    if (i + 1) % 10 == 0:
        print(f"  Processing [{i+1}/{len(products)}]: {product['name'][:40]}...")
    
    embedding = embedding_service.get_product_embedding(product)
    
    points.append(PointStruct(
        id=product['id'],
        vector=embedding,
        payload={
            "name": product['name'],
            "brand": product['brand'],
            "price": product['price'],
            "description": product['description'][:500],
            "category": product['category']
        }
    ))

# Insert into Qdrant
print(f"\n📤 Inserting {len(points)} points into Qdrant...")
success = manager.upsert_points(points, batch_size=20)

if success:
    info = manager.get_collection_info()
    print(f"\n✅ SUCCESS!")
    print(f"   Collection: {info.get('name')}")
    print(f"   Vectors inserted: {info.get('vectors_count')}")
else:
    print("❌ Insertion failed")