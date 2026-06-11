from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from database import connect_db
import os 

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/cctv')
def cctv():
    return render_template('cctv.html')

@app.route('/analisis')
def analisis():
    return render_template('analisis.html')


@app.route('/api/traffic', methods=['GET'])
def get_traffic_data():
    db = connect_db()

    if db is None:
        return jsonify({
            "status": "error",
            "message": "Koneksi database gagal"
        }), 500

    cursor = None

    try:
        date = request.args.get("date")
        cursor = db.cursor(dictionary=True)

        if date:
            query = """
                SELECT 
                    device_id,
                    `object`,
                    HOUR(created_at) AS hour,
                    SUM(CASE WHEN direction = 1 THEN count ELSE 0 END) AS masuk,
                    SUM(CASE WHEN direction = 2 THEN count ELSE 0 END) AS keluar
                FROM object_real_times
                WHERE DATE(created_at) = %s
                GROUP BY device_id, `object`, HOUR(created_at)
                ORDER BY hour, device_id, `object`
            """
            cursor.execute(query, (date,))
        else:
            query = """
                SELECT 
                    device_id,
                    `object`,
                    HOUR(created_at) AS hour,
                    SUM(CASE WHEN direction = 1 THEN count ELSE 0 END) AS masuk,
                    SUM(CASE WHEN direction = 2 THEN count ELSE 0 END) AS keluar
                FROM object_real_times
                GROUP BY device_id, `object`, HOUR(created_at)
                ORDER BY hour, device_id, `object`
            """
            cursor.execute(query)

        results = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

print("Current folder:", os.getcwd())
print("Templates folder ada:", os.path.exists("templates"))
print("Dashboard file ada:", os.path.exists("templates/dashboard.html"))


if __name__ == '__main__':
    app.run(debug=True, port=5000)