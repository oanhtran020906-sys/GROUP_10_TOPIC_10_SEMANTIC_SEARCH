import os
import sys
from pathlib import Path

# Bước 1: Fix lỗi import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import pandas as pd
import psycopg2
from config import settings
from database.postgres import get_db_connection, release_db_connection

BASE_DIR = Path(parent_dir)
CSV_PATH = BASE_DIR / "data" / "raw" / "products.csv"
DATABASE_URL = settings.DATABASE_URL

def initialize_database():
    base_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    conn = psycopg2.connect(base_url)
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Tạo Database nếu chưa có
    try:
        cur.execute("CREATE DATABASE semantic_search")
        print("✅ Đã tạo database semantic_search")
    except psycopg2.errors.DuplicateDatabase:
        print("ℹ️ Database đã tồn tại")

    cur.close()
    conn.close()

    # 2. Kết nối vào database mới tạo để chạy Schema
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Tìm đường dẫn file schema.sql (giả sử nó nằm ở ../database/schema.sql)
    schema_path = os.path.join(BASE_DIR, "database", "schema.sql")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cur.execute(schema_sql)
        print("✅ Đã khởi tạo Schema thành công")
    
    conn.commit()
    cur.close()
    conn.close()

def seed_master_data(cur):
    """Nạp dữ liệu danh mục và ngân sách trước"""
    print("🔄 Đang nạp dữ liệu Categories và Budgets...")
    
    # Insert Categories (Sử dụng ON CONFLICT để tránh lỗi nếu chạy lại script nhiều lần)
    categories = ['camera', 'phones', 'smartwatch', 'tablet', 'keyboard', 
                  'monitor', 'earphones', 'laptop', 'mouse', 'speaker']
    for cat in categories:
        cur.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (cat,))

    # Insert Budgets
    budgets = ['low', 'mid', 'lux']
    for b in budgets:
        cur.execute("INSERT INTO budgets (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (b,))
    
    print("✅ Đã chuẩn bị xong dữ liệu nền.")

def seed_postgres():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Nạp dữ liệu Categories và Budgets trước
        seed_master_data(cur)
        
        # 2. Đọc và nạp sản phẩm từ CSV
        print(f"🔄 Đang đọc dữ liệu từ: {CSV_PATH}")
        df = pd.read_csv(CSV_PATH)

        print(f"🚀 Đang bơm {len(df)} sản phẩm vào database...")
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO products (category_id, budget_id, name, brand, price, image_path, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row['category_id'], 
                    row['budget_id'], 
                    row['name'], 
                    row['brand'], 
                    row['price'], 
                    row['image_path'], 
                    row['description']
                )
            )
        
        conn.commit()
        print("🎉 TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC SEED THÀNH CÔNG!")
        cur.close()

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    initialize_database()
    seed_postgres()