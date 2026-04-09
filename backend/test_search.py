import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.qdrant import init_qdrant
from services.embedding_service import embedding_service
from config import settings

print("=" * 60)
print("🔍 SEMANTIC SEARCH TEST")
print("=" * 60)

# Initialize Qdrant
manager = init_qdrant(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    collection_name=settings.QDRANT_COLLECTION_NAME
)

# Test queries
test_queries = [
    "tai nghe chống ồn tốt pin lâu",
    "laptop gaming cấu hình cao", 
    "điện thoại chụp ảnh đẹp",
    "chuột chơi game không dây",
    "áo ấm mùa đông",  # Anti-keyword test
]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    print("-" * 40)
    
    # Generate embedding for query
    query_vector = embedding_service.get_embedding(query)
    
    # Search
    results = manager.search(query_vector, limit=5, score_threshold=0.3)
    
    if results:
        for i, result in enumerate(results, 1):
            score_pct = result.score * 100
            name = result.payload['name']
            price = result.payload['price']
            print(f"  {i}. {name} - {price:,.0f} VND - {score_pct:.1f}% match")
    else:
        print("  ❌ No results found")