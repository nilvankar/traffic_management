import base64
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, request
from ultralytics import YOLO

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "traffic_violations.db"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
MODEL_PATH = BASE_DIR / "models" / "helmet_detection" / "best_violation.pt"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

CLASS_LABELS = [
    "with_helmet",
    "without_helmet",
    "licence_plate",
    "seatbelt",
    "no_seatbelt",
    "car",
    "bike",
    "autorickshaw",
]
VIOLATION_CLASSES = {"without_helmet", "no_seatbelt"}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            source TEXT DEFAULT 'upload',
            violation_types TEXT,
            class_counts TEXT,
            result_image TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()

model = YOLO(str(MODEL_PATH))


def save_violation_record(image_name, result_path, violations, class_counts, source="upload"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO violations (image_name, source, violation_types, class_counts, result_image, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            image_name,
            source,
            ",".join(violations),
            json.dumps(class_counts),
            str(result_path),
            "Verified" if violations else "Clear",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    if username == "admin" and password == "admin":
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.get("/api/stats")
def dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    counts = conn.execute(
        """
        SELECT
            COUNT(*) AS total_violations,
            SUM(CASE WHEN status = 'Verified' THEN 1 ELSE 0 END) AS today_violations,
            SUM(CASE WHEN violation_types LIKE '%without_helmet%' THEN 1 ELSE 0 END) AS helmet_violations,
            SUM(CASE WHEN violation_types LIKE '%no_seatbelt%' THEN 1 ELSE 0 END) AS seatbelt_violations
        FROM violations
        """
    ).fetchone()
    conn.close()

    total, today, helmets, seatbelts = counts
    return jsonify(
        {
            "total_violations": total or 0,
            "today_violations": today or 0,
            "helmet_violations": helmets or 0,
            "seatbelt_violations": seatbelts or 0,
            "active_cameras": 8,
            "system_status": "Online",
        }
    )


@app.get("/api/violations")
def violations_history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT id, image_name AS location, violation_types AS violation_type, created_at AS timestamp,
               status, source
        FROM violations
        ORDER BY created_at DESC
        LIMIT 50
        """
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(
            {
                "id": row[0],
                "location": row[1],
                "violation_type": row[2],
                "timestamp": row[3],
                "status": row[4],
                "source": row[5],
            }
        )
    return jsonify({"violations": result})


@app.post("/detect")
def detect():
    uploaded_file = request.files.get("image")

    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({"error": "No image uploaded"}), 400

    image_bytes = uploaded_file.read()
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Invalid image"}), 400

    results = model.predict(frame, conf=0.15, verbose=False, iou=0.45)
    result = results[0]

    class_counts = {label: 0 for label in CLASS_LABELS}
    detected_violations = []

    if result.boxes is not None:
        for class_id in result.boxes.cls.cpu().numpy().astype(int):
            if 0 <= class_id < len(CLASS_LABELS):
                label = CLASS_LABELS[class_id]
                class_counts[label] += 1
                if label in VIOLATION_CLASSES:
                    detected_violations.append(label)

    annotated_frame = result.plot()
    success, encoded_image = cv2.imencode(".jpg", annotated_frame)
    if not success:
        return jsonify({"error": "Could not encode annotated image"}), 500

    result_filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    result_path = OUTPUTS_DIR / result_filename
    cv2.imwrite(str(result_path), annotated_frame)

    save_violation_record(
        uploaded_file.filename,
        str(result_path),
        sorted(set(detected_violations)),
        class_counts,
        source="upload",
    )

    image_b64 = base64.b64encode(encoded_image.tobytes()).decode("utf-8")

    return jsonify(
        {
            "status": "success",
            "image_b64": image_b64,
            "result_image": str(result_path),
            "violations": sorted(set(detected_violations)),
            "total_violations": len(detected_violations),
            "class_counts": class_counts,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)