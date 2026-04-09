import os
import sys
from pathlib import Path

# Bước 1: Fix lỗi import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import pandas as pd
from database.postgres import get_db_connection, release_db_connection

BASE_DIR = Path(parent_dir)
CSV_PATH = BASE_DIR / "data" / "raw" / "products.csv"

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
    seed_postgres()