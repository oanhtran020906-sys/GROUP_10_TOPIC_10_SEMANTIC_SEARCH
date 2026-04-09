#!/usr/bin/env python
import sys
import os
import pandas as pd
import time
from typing import List, Dict
from qdrant_client.models import PointStruct

# Thêm đường dẫn để import từ thư mục cha
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.qdrant import init_qdrant, get_qdrant_manager
from services.embedding_service import embedding_service
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_products_from_csv(csv_path: str) -> List[Dict]:
    """Load products from CSV file"""
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.replace('\ufeff', '')
        products = []
        
        category_map = {
            1: "Camera", 2: "Điện thoại", 3: "Smartwatch", 4: "Tablet",
            5: "Bàn phím", 6: "Màn hình", 7: "Tai nghe", 8: "Laptop",
            9: "Chuột", 10: "Loa"
        }
        
        for idx, row in df.iterrows():
            price_str = str(row.get('price', '0')).replace(',', '').strip()
            try:
                price = float(price_str)
            except:
                price = 0
            
            product = {
                "id": idx + 1,
                "name": str(row.get('name', '')),
                "brand": str(row.get('brand', '')) if pd.notna(row.get('brand')) else "Unknown",
                "price": price,
                "description": str(row.get('description', '')),
                "category_id": int(row.get('category_id', 0)) if pd.notna(row.get('category_id')) else 0,
                "image_path": str(row.get('image_path', ''))
            }
            product["category"] = category_map.get(product["category_id"], "Other")
            
            if product['name'] and product['name'] != 'nan':
                products.append(product)
        
        logger.info(f"✅ Loaded {len(products)} products from {csv_path}")
        return products
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        return []


def main():
    logger.info("=" * 60)
    logger.info("🚀 PRODUCT EMBEDDING & INSERTION SCRIPT")
    logger.info("=" * 60)
    
    # Check API key
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE":
        logger.error("❌ Please set your OpenAI API key in backend/.env file")
        logger.info("   Get your API key from: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    # Initialize Qdrant
    manager = init_qdrant(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name=settings.QDRANT_COLLECTION_NAME
    )
    
    # Delete old collection if exists
    if manager.collection_exists():
        logger.info("Deleting existing collection...")
        manager.delete_collection()
        time.sleep(1)
    
    # Create new collection
    manager.create_collection(vector_size=settings.TEXT_EMBEDDING_DIMENSION)
    
    # Find CSV file
    csv_paths = [
        "products.csv",
        "../products.csv",
        "../../products.csv",
        "backend/data/raw/products.csv",
        "data/raw/products.csv"
    ]
    
    products = []
    for path in csv_paths:
        if os.path.exists(path):
            logger.info(f"Found CSV at: {path}")
            products = load_products_from_csv(path)
            if products:
                break
    
    if not products:
        logger.error("❌ No product data found!")
        logger.info("Please place your products.csv in the backend/scripts/ folder")
        sys.exit(1)
    
    # Show statistics
    logger.info(f"\n📊 Product Statistics:")
    logger.info(f"  Total products: {len(products)}")
    
    categories = {}
    for p in products:
        cat = p['category']
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in list(categories.items())[:10]:
        logger.info(f"  - {cat}: {count} products")
    
    # Generate embeddings and insert
    logger.info(f"\n🔄 Generating embeddings using OpenAI...")
    logger.info(f"   Model: {settings.TEXT_EMBEDDING_MODEL}")
    logger.info(f"   Dimension: {settings.TEXT_EMBEDDING_DIMENSION}")
    
    points = []
    failed = []
    
    for i, product in enumerate(products):
        try:
            if (i + 1) % 20 == 0:
                logger.info(f"  Processing [{i+1}/{len(products)}]: {product['name'][:40]}...")
            
            embedding = embedding_service.get_product_embedding(product)
            
            payload = {
                "name": product['name'],
                "brand": product['brand'],
                "price": product['price'],
                "description": product['description'][:500],
                "category": product['category'],
                "category_id": product['category_id'],
                "image_path": product['image_path']
            }
            
            points.append(PointStruct(id=product['id'], vector=embedding, payload=payload))
            
        except Exception as e:
            logger.error(f"  Failed: {product['name']} - {e}")
            failed.append(product['name'])
            continue
    
    if points:
        logger.info(f"\n📤 Inserting {len(points)} points into Qdrant...")
        success = manager.upsert_points(points, batch_size=20)
        
        if success:
            info = manager.get_collection_info()
            logger.info(f"\n✅ SUCCESS!")
            logger.info(f"   Collection: {info.get('name')}")
            logger.info(f"   Status: {info.get('status')}")
            logger.info(f"   Vectors inserted: {info.get('vectors_count')}")
            
            if failed:
                logger.warning(f"⚠️ Failed products: {len(failed)}")
        else:
            logger.error("❌ Insertion failed")
    else:
        logger.error("❌ No points generated")


if __name__ == "__main__":
    main()