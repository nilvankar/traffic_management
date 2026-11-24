import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "traffic_violations.db"


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute(
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


def save_violation(
    image_name,
    result_path,
    violations,
    class_counts,
    source="upload",
    created_at=None,
):
    violation_types = [
        item["type"] if isinstance(item, dict) else str(item)
        for item in violations
    ]
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO violations
                    (image_name, source, violation_types, class_counts, result_image, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    image_name,
                    source,
                    ",".join(sorted(set(violation_types))),
                    json.dumps(class_counts),
                    str(result_path),
                    "Verified" if violation_types else "Clear",
                    created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )


def get_violations(limit=50):
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, image_name, source, violation_types, class_counts,
                   result_image, status, created_at
            FROM violations
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_stats():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_violations,
                SUM(CASE WHEN status = 'Verified' THEN 1 ELSE 0 END) AS today_violations,
                SUM(CASE WHEN violation_types LIKE '%without_helmet%' THEN 1 ELSE 0 END) AS helmet_violations,
                SUM(CASE WHEN violation_types LIKE '%no_seatbelt%' THEN 1 ELSE 0 END) AS seatbelt_violations
            FROM violations
            """
        ).fetchone()
    return {
        "total_violations": row[0] or 0,
        "today_violations": row[1] or 0,
        "helmet_violations": row[2] or 0,
        "seatbelt_violations": row[3] or 0,
        "active_cameras": 8,
        "system_status": "Online",
    }
