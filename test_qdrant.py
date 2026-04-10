import sys
import os
# Thêm dòng này để thư mục backend vào đường dẫn
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.qdrant import qdrant_manager

def test_connection():
    """Kiểm tra kết nối đến Qdrant"""
    try:
        # Kiểm tra collections
        collections = qdrant_manager.client.get_collections()
        print("✅ Kết nối thành công đến Qdrant!")
        print(f"📊 Danh sách collections: {[c.name for c in collections.collections]}")
        
        # Tạo collection test nếu chưa có
        qdrant_manager.create_collection_if_not_exists(vector_size=768)
        
        # Test thêm một vector
        test_vector = [0.1] * 768  # Vector test với 768 chiều
        qdrant_manager.insert_vector(
            point_id="test_1",
            vector=test_vector,
            payload={"name": "Sản phẩm test", "price": 100000}
        )
        print("✅ Đã thêm vector test thành công!")
        
        # Test tìm kiếm
        results = qdrant_manager.search(query_vector=test_vector, limit=1)
        print(f"✅ Tìm kiếm thành công, kết quả: {len(results)} items")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False

if __name__ == "__main__":
    test_connection()