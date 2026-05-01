import mysql.connector
import uuid
from datetime import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cctv_vehicle",
        autocommit=True
    )

def save_to_db(object_name, direction, device):
    try:
        db = connect_db()
        cursor = db.cursor(buffered=True)
        query = """
        INSERT INTO object_real_times
        (id, `object`, count, start_date, end_date, created_at, email, direction, device_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        values = (str(uuid.uuid4()), object_name, 1, now, now, now, "ai@traffic.com", direction, device)
        cursor.execute(query, values)
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Database Error: {e}")