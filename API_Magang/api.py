from flask import Flask, jsonify
from flask_cors import CORS
from database import connect_db

app = Flask(__name__)
CORS(app)

@app.route('/api/traffic', methods=['GET'])
def get_traffic_data():
    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT device_id, object,
               SUM(CASE WHEN direction = 1 THEN 1 ELSE 0 END) as masuk,
               SUM(CASE WHEN direction = 2 THEN 1 ELSE 0 END) as keluar
        FROM object_real_times
        GROUP BY device_id, object
        """
        cursor.execute(query)
        results = cursor.fetchall()
        db.close()
        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)