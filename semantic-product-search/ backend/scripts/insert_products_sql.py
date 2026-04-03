import json
from database.postgres import get_connection

def insert_products():
    conn = get_connection()
    cursor = conn.cursor()

    with open("data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    for p in products:
        cursor.execute("""
            INSERT INTO products (id, name, description, price, category, brand, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            p["id"],
            p["name"],
            p["description"],
            p["price"],
            p["category"],
            p["brand"],
            p["image_url"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print("Inserted into PostgreSQL!")

if __name__ == "__main__":
    insert_products()
