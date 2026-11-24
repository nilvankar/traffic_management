# MetroPolis: AI Traffic Violation Detection

**Live demo:** https://nilvankar-traffic-management-app-gjwhfx.streamlit.app/
**Demo video:** https://www.youtube.com/watch?v=WSG1gTsjwjI
**Backend (Flask API and model):** https://github.com/nilvankar/Metropolicis-backend

MetroPolis detects **helmet violations** (two-wheelers) and **seatbelt violations** (cars) from traffic images and video. Each violation is logged with a timestamp and shown on a dashboard.

## Features
- YOLOv26 model trained on a dataset of about 10,000 Indian road traffic images
- Helmet and seatbelt violation detection from images and video
- Violations stored with timestamps in a SQLite database
- Streamlit dashboard to view detections and logged violations
- Flask REST API for detection and data access (in the backend repository)

## Tech Stack
Python, YOLOv8, OpenCV, Flask, SQLite, Streamlit

## How It Works
1. The user uploads an image or video in the Streamlit dashboard.
2. The YOLOv8 model detects riders, helmets, drivers and seatbelts.
3. Violations are logged with a timestamp in SQLite.
4. The dashboard shows the annotated output and the violation log.

## Results
| Metric | Value |
|---|---|
| mAP@0.5 | _add your value_ |
| Precision | _add your value_ |
| Recall | _add your value_ |

## Screenshots
![Helmet_Violatoin](Screenshot (14).png)
![Helmet_Violatoin_number_plate](Screenshot (15).png)
![Car_seatbelt](Screenshot (16).png)

## Run Locally
```bash
git clone https://github.com/nilvankar/traffic_management.git
cd traffic_management
pip install -r requirements.txt
streamlit run app.py
```

## Project Context
Built during the SAP Code Unnati program (Edunet Foundation x SAP).
_Add your role and teammates here if it was a team project._

## Author
Neel Vankar | [LinkedIn](https://linkedin.com/in/neel-vankar-7baa5624b) | [GitHub](https://github.com/nilvankar)
