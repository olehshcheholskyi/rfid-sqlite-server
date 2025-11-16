import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

RENDER_DISK_PATH = "/var/data/data.db"
LOCAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')

if os.environ.get('IS_RENDER') == 'true':
    db_path = f"sqlite:///{RENDER_DISK_PATH}"
    print(f"Використовую постійний диск Render: {db_path}")
else:
    db_path = f"sqlite:///{LOCAL_PATH}"
    print(f"Запускаю локально, база даних: {db_path}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = db_path
db = SQLAlchemy(app)

class DeviceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_data = db.Column(db.String(100), nullable=False)
    client_data = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    if not data or 'deviceData' not in data or 'clientData' not in data:
        return jsonify({"status": "error", "message": "Invalid data format"}), 400

    try:
        new_log = DeviceLog(
            device_data=data['deviceData'],
            client_data=data['clientData']
        )
        db.session.add(new_log)
        db.session.commit()
        print(f"Успішно збережено в SQLite: Device={data['deviceData']}, Client={data['clientData']}")
        return jsonify({"status": "success", "message": "Data saved to SQLite"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Помилка збереження в SQLite: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port, debug=True)