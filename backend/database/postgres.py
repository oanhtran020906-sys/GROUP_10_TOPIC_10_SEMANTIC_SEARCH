 # PostgreSQL connection
import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Load các biến từ file .env (User, Password, Host...)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/semantic_search")

try:
    # Tạo một Connection Pool để quản lý nhiều kết nối cùng lúc cho FastAPI
    postgre_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # Số kết nối tối thiểu
        20, # Số kết nối tối đa
        dsn=DATABASE_URL
    )
    print("✅ Kết nối PostgreSQL thành công qua Pool!")
except Exception as e:
    print(f"❌ Lỗi khi kết nối PostgreSQL: {e}")

# Hàm này để lấy một kết nối từ Pool ra dùng
def get_db_connection():
    return postgre_pool.getconn()

# Hàm này để trả kết nối lại cho Pool sau khi dùng xong
def release_db_connection(conn):
    postgre_pool.putconn(conn)