 # PostgreSQL connection
import psycopg2
from psycopg2 import pool
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

DATABASE_URL = settings.DATABASE_URL

try:
    postgre_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # Số kết nối tối thiểu
        20, # Số kết nối tối đa
        dsn=DATABASE_URL
    )
    print("✅ Kết nối PostgreSQL thành công qua Pool!")
except Exception as e:
    print(f"❌ Lỗi khi kết nối PostgreSQL: {e}")

def get_db_connection():
    return postgre_pool.getconn()

def release_db_connection(conn):
    postgre_pool.putconn(conn)