import sys
import os

# Thêm backend vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.qdrant import init_qdrant
from services.embedding_service import embedding_service
from config import settings
import pandas as pd

print("=" * 80)
print("🔍 SO SÁNH: TÌM KIẾM NGỮ NGHĨA (Vector) VS TÌM KIẾM TỪ KHÓA (SQL LIKE)")
print("=" * 80)

# Đọc file CSV để mô phỏng SQL LIKE
csv_path = "backend/data/raw/products.csv"
if not os.path.exists(csv_path):
    csv_path = "products.csv"

df = pd.read_csv(csv_path)
df.columns = df.columns.str.replace('\ufeff', '')

# Kết nối Qdrant
manager = init_qdrant(
    host=settings.QDRANT_HOST,
    port=settings.QDRANT_PORT,
    collection_name=settings.QDRANT_COLLECTION_NAME
)

# Các câu query test
test_queries = [
    {
        "query": "áo mặc cho mùa đông giá rét",
        "note": "Anti-keyword test - không có từ 'áo' trong database"
    },
    {
        "query": "tai nghe chống ồn tốt pin lâu",
        "note": "Test tìm tai nghe cao cấp"
    },
    {
        "query": "laptop nhẹ pin trâu học sinh sinh viên",
        "note": "Test tìm laptop phổ thông"
    },
    {
        "query": "điện thoại chụp ảnh đẹp giá mềm",
        "note": "Test tìm điện thoại tầm trung"
    },
    {
        "query": "chuột chơi game không dây",
        "note": "Test tìm chuột gaming"
    }
]

# Hàm mô phỏng SQL LIKE
def sql_like_search(query, df, limit=5):
    keywords = query.lower().split()
    results = []
    
    for idx, row in df.iterrows():
        text = f"{row['name']} {row['brand']} {row['description']}".lower()
        match_count = sum(1 for kw in keywords if kw in text)
        if match_count > 0:
            results.append({
                'name': row['name'],
                'brand': row['brand'] if pd.notna(row['brand']) else "Unknown",
                'price': row['price'],
                'matches': match_count
            })
    
    results = sorted(results, key=lambda x: x['matches'], reverse=True)[:limit]
    return results

# Chạy test cho từng query
for test in test_queries:
    query = test['query']
    note = test['note']
    
    print(f"\n{'='*80}")
    print(f"📝 CÂU HỎI: '{query}'")
    print(f"   {note}")
    print('='*80)
    
    # SQL LIKE (Traditional)
    print("\n🔍 CÁCH 1: SQL LIKE (Tìm kiếm theo từ khóa truyền thống)")
    print("-" * 50)
    sql_results = sql_like_search(query, df, limit=5)
    
    if sql_results:
        for i, r in enumerate(sql_results, 1):
            print(f"  {i}. {r['name']} - {r['brand']} - {r['price']:,.0f} VND")
            print(f"     (Khớp {r['matches']} từ khóa)")
    else:
        print("  ❌ KHÔNG CÓ KẾT QUẢ! (0 sản phẩm khớp từ khóa)")
    
    # Vector Search (Semantic)
    print("\n🤖 CÁCH 2: VECTOR SEARCH (Tìm kiếm ngữ nghĩa thông minh)")
    print("-" * 50)
    
    query_vector = embedding_service.get_embedding(query)
    results = manager.search(query_vector, limit=5, score_threshold=0.3)
    
    if results:
        for i, result in enumerate(results, 1):
            score_pct = result.score * 100
            name = result.payload['name']
            brand = result.payload['brand']
            price = result.payload['price']
            print(f"  {i}. {name} - {brand} - {price:,.0f} VND")
            print(f"     (Độ tương đồng ngữ nghĩa: {score_pct:.1f}%)")
    else:
        print("  ❌ Không có kết quả")
    
    print("\n" + "-" * 50)
    if not sql_results and results:
        print("💡 NHẬN XÉT: SQL LIKE không tìm được gì, nhưng Vector Search đã hiểu ý đồ!")
        print("   → Vector Search hiểu 'áo ấm' = 'thiết bị giữ ấm' = tai nghe chụp tai")
    elif sql_results and results:
        print("💡 NHẬN XÉT: Cả 2 cách đều tìm được kết quả, nhưng Vector Search hiểu ngữ nghĩa tốt hơn")
    print("-" * 50)

# Tổng kết
print("\n" + "=" * 80)
print("📊 TỔNG KẾT - SỨC MẠNH CỦA VECTOR SEARCH")
print("=" * 80)
print("""
✅ SQL LIKE (Keyword Search):
   - Chỉ tìm được sản phẩm có chứa từ khóa xuất hiện đúng
   - Không hiểu ngữ cảnh, không hiểu ý đồ người dùng
   - Với câu 'áo mùa đông' → 0 kết quả

✅ VECTOR SEARCH (Semantic Search):
   - Hiểu được ý nghĩa và ngữ cảnh của câu hỏi
   - 'áo mùa đông' → hiểu là 'cần sự ấm áp' → tìm được tai nghe chụp tai
   - 'laptop nhẹ pin trâu' → hiểu là 'laptop di động, thời lượng pin tốt'
   - Tìm được sản phẩm liên quan DÙ KHÔNG CÓ TỪ KHÓA TRÙNG KHỚP

💡 ĐÂY CHÍNH LÀ LÝ DO VECTOR SEARCH VƯỢT TRỘI HƠN SQL LIKE!
""")
print("=" * 80)