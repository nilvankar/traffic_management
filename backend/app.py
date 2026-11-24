import base64
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, request

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db import get_stats, get_violations, init_db, save_violation
from detector import detect_with_counts, load_model

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

init_db()
model = load_model()


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
    return jsonify(get_stats())


@app.get("/api/violations")
def violations_history():
    result = []
    for row in get_violations():
        result.append(
            {
                "id": row["id"],
                "location": row["image_name"],
                "violation_type": row["violation_types"],
                "timestamp": row["created_at"],
                "status": row["status"],
                "source": row["source"],
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

    annotated_frame, detected_violations, class_counts = detect_with_counts(frame, model=model)
    violation_types = sorted({item["type"] for item in detected_violations})
    success, encoded_image = cv2.imencode(".jpg", annotated_frame)
    if not success:
        return jsonify({"error": "Could not encode annotated image"}), 500

    result_filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    result_path = OUTPUTS_DIR / result_filename
    cv2.imwrite(str(result_path), annotated_frame)

    save_violation(
        uploaded_file.filename,
        str(result_path),
        violation_types,
        class_counts,
        source="upload",
    )

    image_b64 = base64.b64encode(encoded_image.tobytes()).decode("utf-8")

    return jsonify(
        {
            "status": "success",
            "image_b64": image_b64,
            "result_image": str(result_path),
            "violations": violation_types,
            "total_violations": len(detected_violations),
            "class_counts": class_counts,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)