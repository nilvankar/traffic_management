from datetime import datetime
from functools import lru_cache
from pathlib import Path

import cv2
from ultralytics import YOLO

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "backend"
    / "models"
    / "helmet_detection"
    / "best_violation.pt"
)

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


@lru_cache(maxsize=1)
def load_model():
    return YOLO(str(MODEL_PATH))


def detect_with_counts(image, model=None):
    if model is None:
        model = load_model()
    result = model.predict(image, conf=0.15, verbose=False, iou=0.45)[0]
    class_counts = {label: 0 for label in CLASS_LABELS}
    violations = []

    if result.boxes is not None:
        class_ids = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for class_id, confidence in zip(class_ids, confidences):
            if 0 <= class_id < len(CLASS_LABELS):
                label = CLASS_LABELS[class_id]
                class_counts[label] += 1
                if label in VIOLATION_CLASSES:
                    violations.append(
                        {
                            "type": label,
                            "confidence": float(confidence),
                            "timestamp": timestamp,
                        }
                    )

    return result.plot(), violations, class_counts


def detect(image, model=None):
    annotated_image, violations, _ = detect_with_counts(image, model=model)
    return annotated_image, violations


def resize_image(image, max_side=640):
    height, width = image.shape[:2]
    scale = min(1.0, max_side / max(height, width))
    if scale == 1.0:
        return image
    return cv2.resize(
        image,
        (round(width * scale), round(height * scale)),
        interpolation=cv2.INTER_AREA,
    )
