from postgres import get_db_connection, release_db_connection

try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    record = cur.fetchone()
    print(f"Bạn đang kết nối tới: {record}")
    cur.close()
    release_db_connection(conn)
except Exception as e:
    print(f"Kết nối thất bại: {e}")