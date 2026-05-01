import mysql.connector
import uuid
from datetime import datetime

def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cctv_db"
        )
    except mysql.connector.Error as err:
        print(f"Koneksi DB gagal: {err}")
        return None


def save_to_db(object_name, direction, device):
    db = connect_db()
    
    if db is None:
        return

    cursor = None
    try:
        cursor = db.cursor()

        query = """
        INSERT INTO object_real_times
        (id, `object`, count, start_date, end_date, created_at, email, direction, device_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        now = datetime.now()

        values = (
            str(uuid.uuid4()),   # id
            object_name,         # object
            1,                   # count
            now,                 # start_date
            now,                 # end_date
            now,                 # created_at
            "ai@traffic.com",    # email
            direction,           # 1 masuk / 2 keluar
            device               # CCTV2
        )

        cursor.execute(query, values)
        db.commit()  # ✅ commit manual (lebih aman)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if db.is_connected():
            db.close()