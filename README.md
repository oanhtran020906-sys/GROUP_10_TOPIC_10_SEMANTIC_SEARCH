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

---

## 🚀 Hướng dẫn cài đặt & Kết nối

### 2. Khởi tạo môi trường Backend


Di chuyển vào thư mục backend và tạo môi trường ảo:
```bash
cd backend
```

Điều chỉnh file .evn
Copy file: Chạy lệnh 
```bash
cp .env.example .env
```
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


# Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3. Triển khai Database (Docker)
Nếu bạn đã cài Docker, chỉ cần một câu lệnh duy nhất để dựng Postgres và Qdrant:

```bash
docker-compose up -d
```

Lưu ý: Nếu không dùng Docker, bạn phải tự cài Postgres (cổng 5432) và Qdrant (cổng 6333) cục bộ.