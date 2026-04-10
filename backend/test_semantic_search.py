"""
Test semantic search với Sentence-Transformers
Không cần OpenAI, hoàn toàn miễn phí
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.qdrant import qdrant_store
from backend.services.embedding_service import embedding_service

def main():
    print("=" * 70)
    print("🔍 SEMANTIC SEARCH WITH SENTENCE-TRANSFORMERS")
    print("=" * 70)
    
    # Set embedding service
    qdrant_store.set_embedding_service(embedding_service)
    
    # Kiểm tra collection
    try:
        stats = qdrant_store.get_collection_stats()
        print(f"\n📊 Collection stats:")
        print(f"   - Tên: {stats['name']}")
        print(f"   - Vector size: {stats['vector_size']}")
        print(f"   - Số sản phẩm: {stats['points_count']}")
    except Exception as e:
        print(f"\n⚠️ Collection chưa có dữ liệu: {e}")
        print("   Chạy script insert trước nhé!")
        return
    
    # Test queries
    test_queries = [
        "áo ấm mặc mùa đông",
        "giày thể thao chạy bộ",
        "quần jeans nam đẹp",
        "tai nghe bluetooth không dây",
        "điện thoại pin trâu chụp ảnh đẹp"
    ]
    
    print("\n" + "=" * 70)
    print("🔍 KẾT QUẢ TÌM KIẾM")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        print("-" * 50)
        
        # Tạo embedding cho query
        query_vector = embedding_service.encode_text(query)
        
        # Tìm kiếm
        results = qdrant_store.semantic_search(
            query_vector=query_vector,
            limit=3,
            score_threshold=0.3
        )
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['name']}")
                print(f"     📂 {r['category']} | 💰 {r['price']:,.0f}đ")
                print(f"     🎯 Similarity: {r['similarity_percent']}%")
                print()
        else:
            print("  ❌ Không tìm thấy kết quả\n")

if __name__ == "__main__":
    main()