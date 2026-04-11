# 🛒 Semantic Product Search (Topic 10)

Hệ thống tìm kiếm sản phẩm thông minh dành cho Laptop và Phụ kiện, sử dụng công nghệ Vector Search (Qdrant) so sánh song song với SQL Search truyền thống (PostgreSQL).

## 🌟 Tính năng chính
- **Search Anti-Keyword**: Tìm kiếm theo nhu cầu thay vì từ khóa chính xác (VD: "máy tính cho sinh viên IT mỏng nhẹ").
- **Comparison UI**: So sánh trực quan kết quả giữa PostgreSQL (LIKE) và Qdrant (Semantic).
- **Multimodal Search**: Tìm kiếm sản phẩm tương tự bằng cách tải lên hình ảnh (CLIP model).
- **Hybrid Database**: Kết hợp sức mạnh dữ liệu quan hệ (Postgres) và dữ liệu vector (Qdrant).

---

## 🛠 Yêu cầu hệ thống
- **Python**: 3.9+ (khuyến khích 3.11)
- **Docker & Docker Compose** (Khuyến khích)
- **Node.js & npm** (Để chạy Frontend React)
- **PostgreSQL:** 9+
- **Qdrant**

---

## 🚀 Hướng dẫn cài đặt & Kết nối

### 1. Khởi tạo môi trường Backend

Di chuyển vào thư mục backend và tạo môi trường ảo:
```bash
cd backend
```

Điều chỉnh file .env. Copy file: Chạy lệnh 
```bash
cp .env.example .env
```
Sau khi copy xong, điều chỉnh tham số cho phù hợp với máy

Tạo môi trường python ảo
```bash
python -m venv venv
```
Hoặc dùng Anaconda
```bash
conda create --name searchenv python=3.11
```

Kích hoạt venv (môi trường python)
```bash
# Kích hoạt venv (Windows)
venv\Scripts\activate
# Kích hoạt venv (macOS/Linux)
source venv/bin/activate
# Kích hoạt trên Anaconda
conda activate searchenv
```

Cài đặt thư viện
```bash
pip install -r requirements.txt
```
Lưu ý cho team: nếu import thư viện gì mới thì bổ sung vào file backend/requirements.txt

### 2. Triển khai Database
Nếu bạn đã cài Docker, chỉ cần một câu lệnh duy nhất để dựng Postgres và Qdrant:

```bash
# hiện tại chưa có cái này, nhg sau sẽ viết
docker-compose up -d
```

Lưu ý: Nếu không dùng Docker, bạn phải tự cài Postgres (cổng 5432) và Qdrant (cổng 6333) cục bộ.

Nếu bạn chưa cài Docker. 
1. Postgre
Mở pgAdmin4, mở file database/schema.sql. chạy dòng
```bash
CREATE DATABASE semantic_search;
```

Đổi connection sang sematic_search database, chạy các dòng còn lại.

Quay lại terminal, chạy dòng dưới để thêm data sample vào database

```bash
python scripts/seed_db.py
```

2. Qdrant
Chạy file qdrant.exe trên máy
Để feed sample data vào Qdrant, mở terminal chạy lần lượt:
``` bash
python scripts\create_collection.py

python scripts\insert_products_vector.py
```

### 3.chạy web
```bash
python main.py
```
mở file frontend2/index.html
