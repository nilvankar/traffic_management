from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from db import get_violations, init_db, save_violation
from detector import detect, load_model, resize_image

ROOT_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = ROOT_DIR / "samples"

st.set_page_config(
    page_title="MetroPolis",
    page_icon="🚦",
    layout="wide",
)


@st.cache_resource
def get_model():
    return load_model()


init_db()

st.markdown(
    """
    <style>
    :root {
        --bg: #061a2d;
        --card: #0d2340;
        --primary: #38bdf8;
        --primary-strong: #0ea5e9;
        --accent: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --text: #e2e8f0;
        --muted: #94a3b8;
    }
    .stApp {
        background: linear-gradient(135deg, #061a2d 0%, #0c1d31 30%, #111827 100%);
        color: var(--text);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: rgba(12, 29, 49, 0.92);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }
    .stTabs [role="tablist"] {
        gap: 0.5rem;
    }
    .stTabs [role="tab"] {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 10px 10px 0 0;
        color: var(--text);
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, rgba(56,189,248,0.2), rgba(15,23,42,0.95));
        border-bottom: 2px solid var(--primary);
    }
    div[data-testid="stMetricValue"] {
        color: white;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("MetroPolis")
st.caption("AI-assisted traffic safety image analysis.")

sample_files = (
    sorted(
        file
        for file in SAMPLES_DIR.iterdir()
        if file.is_file() and file.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    if SAMPLES_DIR.is_dir()
    else []
)
if sample_files:
    image_source = st.radio("Image source", ["Upload an image", "Try sample images"])
else:
    image_source = "Upload an image"

uploaded_image = None
image_name = None
if image_source == "Try sample images":
    selected_sample = st.selectbox("Choose a sample image", sample_files, format_func=lambda path: path.name)
    uploaded_image = Image.open(selected_sample).convert("RGB")
    image_name = selected_sample.name
else:
    uploaded_file = st.file_uploader(
        "Upload a traffic image",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
    )
    if uploaded_file is not None:
        uploaded_image = Image.open(uploaded_file).convert("RGB")
        image_name = uploaded_file.name

if uploaded_image is not None:
    st.image(uploaded_image, caption="Input image", use_container_width=True)
    if st.button("Analyze image", type="primary"):
        image = np.asarray(uploaded_image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = resize_image(image)

        with st.spinner("Running traffic safety detection..."):
            annotated_image, violations = detect(
                image,
                model=get_model(),
            )

        save_violation(
            image_name,
            "",
            violations,
            {},
            source="upload" if image_source == "Upload an image" else "sample",
        )
        st.subheader("Annotated image")
        st.image(annotated_image, channels="BGR", use_container_width=True)
        st.subheader("Detected violations")
        if violations:
            st.dataframe(violations, use_container_width=True, hide_index=True)
        else:
            st.info("No violations detected.")

st.subheader("Logged violations")
history = get_violations()
if history:
    st.dataframe(
        [
            {
                "Image": row["image_name"],
                "Violation type": row["violation_types"] or "None",
                "Timestamp": row["created_at"],
                "Status": row["status"],
                "Source": row["source"],
            }
            for row in history
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No logged analyses yet.")
