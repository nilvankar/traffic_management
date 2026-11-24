---
title: MetroPolis
emoji: 🚦
sdk: streamlit
app_file: app.py
pinned: false
---

# MetroPolis

MetroPolis is an AI-assisted traffic safety application that analyzes road images for helmet and seatbelt violations using a YOLO model.

## Features

- Upload JPG, JPEG, or PNG images for analysis.
- View annotated detections and violation type, confidence, and timestamp.
- Review logged analyses from a local SQLite database.
- Try images placed in the optional `samples/` folder.
- Run inference directly in Streamlit without a separate Flask process.

## Tech stack

- Python and Streamlit
- Ultralytics YOLO
- OpenCV
- SQLite
- Flask API (optional for local use)

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The optional Flask API is available from `backend/app.py` for local API use.

The hosted demo supports image upload only; its SQLite demo data resets when the Space restarts.
