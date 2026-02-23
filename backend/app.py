from flask import Flask, request, jsonify
from ultralytics import YOLO
import sqlite3
import os
from datetime import datetime
import cv2
from flask import send_from_directory, jsonify
import glob
app = Flask(__name__)

# -----------------------
# LOAD MODEL (ONLY ONCE)
# -----------------------
model = YOLO("models/helmet_detection/yolo_26_best.pt")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


DB_PATH = "database.db"


# -----------------------
# DATABASE INIT
# -----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS violations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        violation_type TEXT,
        location TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- IMAGE PROCESSING ----------------
def process_image(image_path):

    results = model(image_path)

    annotated = results[0].plot()

    output_path = os.path.join(OUTPUT_FOLDER, "result.jpg")
    cv2.imwrite(output_path, annotated)

    return output_path

def process_video(video_path):

    cap = cv2.VideoCapture(video_path)

    output_path = os.path.join(OUTPUT_FOLDER, "result.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(
        output_path,
        fourcc,
        20,
        (int(cap.get(3)), int(cap.get(4)))
    )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated = results[0].plot()

        out.write(annotated)

    cap.release()
    out.release()

    return output_path



# -----------------------
# LOGIN API
# -----------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    )

    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401


# -----------------------
# VIDEO / IMAGE DETECTION
# -----------------------
@app.route("/upload", methods=["POST"])
def upload():

    try:
        file = request.files["file"]

        upload_path = os.path.join("uploads", file.filename)
        file.save(upload_path)

        # Run YOLO
        results = model(upload_path, save=True)

        # Find latest prediction folder
        predict_folders = glob.glob("runs/detect/predict*")
        latest_folder = max(predict_folders, key=os.path.getctime)

        output_file = os.path.join(latest_folder, file.filename)

        return jsonify({
            "status": "success",
            "result_path": output_file.replace("\\", "/")
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# -----------------------
# DASHBOARD DATA
# -----------------------
@app.route("/api/stats")
def stats():

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    total = c.execute("SELECT COUNT(*) FROM violations").fetchone()[0]

    conn.close()

    return jsonify({
        "total_violations": total,
        "active_cameras": 1,
        "system_status": "Online"
    })

@app.route("/result/<path:filename>")
def get_result(filename):
    return send_from_directory(".", filename)

""" normal run

""" 
# if __name__ == "__main__":
#     app.run(port=5000, debug=True)


"""after deployment"""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)