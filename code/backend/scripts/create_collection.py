"""
Tạo collection tech_products trong Qdrant
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from services.embedding_service import embedding_service

COLLECTION_NAME = settings.QDRANT_COLLECTION_NAME
QDRANT_PATH = settings.QDRANT_DATA_PATH

def create_collection():
    """Tạo collection mới trong Qdrant"""
    
    print("=" * 60)
    print(f"📁 CREATING QDRANT COLLECTION: {COLLECTION_NAME}")
    print("=" * 60)
    
    # Kết nối Qdrant
    os.makedirs(QDRANT_PATH, exist_ok=True)
    client = QdrantClient(path=QDRANT_PATH)
    print(f"✅ Connected to Qdrant (local mode)")
    print(f"   📁 Storage: {os.path.abspath(QDRANT_PATH)}")
    
    # Lấy vector size
    vector_size = embedding_service.get_vector_size()
    print(f"\n📐 Vector size: {vector_size}")
    print(f"📁 Collection name: {COLLECTION_NAME}")
    
    # Xóa collection cũ nếu tồn tại
    if client.collection_exists(COLLECTION_NAME):
        print(f"\n🗑️ Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)
        print("   ✅ Deleted")
    
    # Tạo collection mới
    print(f"\n📁 Creating collection: {COLLECTION_NAME}")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )
    
    print(f"\n✅ Collection created successfully!")
    print(f"   📐 Vector size: {vector_size}")
    print(f"   📏 Distance: Cosine")
    print(f"   🏷️  Collection name: {COLLECTION_NAME}")
    
    return True


def check_collection():
    """Kiểm tra collection"""
    client = QdrantClient(path=QDRANT_PATH)
    
    if client.collection_exists(COLLECTION_NAME):
        info = client.get_collection(COLLECTION_NAME)
        print(f"\n✅ Collection '{COLLECTION_NAME}' exists:")
        print(f"   📊 Points: {info.points_count}")
        print(f"   📐 Vector size: {info.config.params.vectors.size}")
        return True
    else:
        print(f"\n❌ Collection '{COLLECTION_NAME}' does not exist")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check if collection exists")
    args = parser.parse_args()
    
    if args.check:
        check_collection()
    else:
        create_collection()