from db import get_db_connection

try:
    conn = get_db_connection()
    print(" DB Connected Successfully")
    conn.close()
except Exception as e:
    print(" DB Connection Failed:", e)
