import pandas as pd
import os
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_service import image_embedding_service
from config import settings

def setup_image_collection():
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    collection_name = settings.QDRANT_IMG_COLLECTION

    print(f"🚀 Đang tạo collection: {collection_name}...")
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=512,
            distance=models.Distance.COSINE
        )
    )

    BASE_DIR = Path(__file__).resolve().parent.parent
    csv_path = os.path.join(BASE_DIR, 'data', 'raw', 'products.csv')
    image_base_path = os.path.join(BASE_DIR, 'data', 'images')


    df = pd.read_csv(csv_path)
    print(f"Tìm thấy {len(df)} sản phẩm trong CSV.")

    points = []
    
    # Duyệt qua từng dòng để vectorize
    for index, row in df.iterrows():
        product_id = index + 1 # Auto increment từ 1
        img_relative_path = row['image_path']
        full_img_path = os.path.join(image_base_path, img_relative_path)

        if not os.path.exists(full_img_path):
            print(f"⚠️ Không tìm thấy ảnh: {full_img_path}, bỏ qua...")
            continue

        print(f"Đang xử lý sản phẩm {product_id}: {row['name']}...")
        
        # Chuyển ảnh thành vector
        vector = image_embedding_service.get_image_embedding_from_path(str(full_img_path))
        
        if vector:
            points.append(
                models.PointStruct(
                    id=product_id,
                    vector=vector,
                    payload={
                        "product_id": product_id,
                        "name": row['name']
                    }
                )
            )

    # Upload lên Qdrant
    if points:
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print(f"✅ Hoàn tất! Đã lưu {len(points)} vector ảnh vào Qdrant.")
    else:
        print("❌ Không có vector nào được tạo ra.")

if __name__ == "__main__":
    setup_image_collection()