 # PostgreSQL connection
import psycopg2
from psycopg2 import pool
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

DATABASE_URL = settings.DATABASE_URL

postgre_pool = None
def get_db_connection():
    global postgre_pool
    if postgre_pool is None:
        try:
            postgre_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, dsn=DATABASE_URL
            )
            print("✅ Kết nối PostgreSQL thành công qua Pool!")
        except Exception as e:
            print(f"❌ Lỗi khi khởi tạo Pool: {e}")
            raise e
    
    return postgre_pool.getconn()

def release_db_connection(conn):
    global postgre_pool
    if postgre_pool:
        postgre_pool.putconn(conn)
    else:
        conn.close()