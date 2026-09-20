import os
import sqlite3
from pathlib import Path

import pandas as pd
import requests

API_BASE_URL = "http://127.0.0.1:5000"
DB_PATH = Path(__file__).resolve().parent / "backend" / "traffic_violations.db"


def check_login(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"username": username, "password": password},
            timeout=5,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_dashboard_stats():
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass

    return {
        "total_violations": 0,
        "today_violations": 0,
        "helmet_violations": 0,
        "seatbelt_violations": 0,
        "active_cameras": 8,
        "system_status": "Offline",
    }


def get_recent_violations():
    try:
        response = requests.get(f"{API_BASE_URL}/api/violations", timeout=5)
        if response.status_code == 200:
            payload = response.json()
            rows = payload.get("violations", [])
            if rows:
                return pd.DataFrame(rows)
    except requests.RequestException:
        pass

    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql(
                "SELECT image_name AS location, violation_types AS violation_type, created_at AS timestamp, status FROM violations ORDER BY created_at DESC LIMIT 50",
                conn,
            )
            conn.close()
            if not df.empty:
                return df
        except Exception:
            pass

    return pd.DataFrame(
        {
            "timestamp": [],
            "violation_type": [],
            "location": [],
            "status": [],
            "source": [],
        }
    )


def upload_file_to_backend(uploaded_file):
    files = {
        "image": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    try:
        response = requests.post(f"{API_BASE_URL}/detect", files=files, timeout=120)
        data = response.json()
        if response.status_code != 200:
            return {"status": "error", "error": data.get("error", "Detection failed")}
        return data
    except requests.RequestException as exc:
        return {"status": "error", "error": f"Backend unavailable: {exc}"}