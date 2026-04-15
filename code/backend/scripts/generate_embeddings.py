"""
Tạo embeddings cho sản phẩm từ CSV
Sử dụng Sentence-Transformers 2.5.1
"""

import sys
import os

# Thêm đường dẫn backend vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import time
from services.embedding_service import embedding_service
from config import config


def generate_embeddings():
    """Tạo embeddings cho tất cả sản phẩm"""
    
    print("=" * 60)
    print("🔨 GENERATING EMBEDDINGS")
    print("=" * 60)
    
    # Đọc dữ liệu
    csv_path = config.DATA_PATH
    print(f"\n📂 Reading CSV: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        print(f"\n💡 Please check:")
        print(f"   - File exists at: {csv_path}")
        print(f"   - Or update DATA_PATH in .env file")
        return None, None
    
    df = pd.read_csv(csv_path, encoding='utf-8')
    df = df.fillna('')
    print(f"✅ Loaded {len(df)} products")
    print(f"   Columns: {list(df.columns)}")
    
    # Tạo text để embedding
    print("\n🔄 Preparing texts for embedding...")
    texts = []
    for _, row in df.iterrows():
        brand = row['brand'] if row['brand'] else ''
        # Kết hợp name, brand, description
        text = f"{row['name']}. {brand}. {row['description']}"
        texts.append(text)
    
    # Tạo embeddings
    print(f"\n🔄 Generating embeddings using Sentence-Transformers...")
    print(f"   Model: {embedding_service.model_name}")
    print(f"   Vector size: {embedding_service.get_vector_size()}")
    print(f"   Number of products: {len(df)}")
    
    start_time = time.time()
    
    # Tạo embeddings theo batch để tránh quá tải
    batch_size = 50
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embedding_service.encode(batch_texts, normalize=True)
        all_embeddings.append(batch_embeddings)
        print(f"   ✅ Processed {min(i+batch_size, len(texts))}/{len(texts)} texts")
    
    embeddings = np.vstack(all_embeddings)
    elapsed = time.time() - start_time
    
    print(f"\n✅ Embeddings generated!")
    print(f"   ⏱️ Time: {elapsed:.2f} seconds")
    print(f"   📊 Shape: {embeddings.shape}")
    print(f"   ⚡ Speed: {len(df)/elapsed:.1f} products/second")
    
    # Lưu embeddings
    data_dir = os.path.dirname(csv_path)
    if not data_dir:
        data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, 'embeddings.npy')
    np.save(output_path, embeddings)
    print(f"💾 Saved embeddings to: {output_path}")
    
    return embeddings, df


if __name__ == "__main__":
    generate_embeddings()