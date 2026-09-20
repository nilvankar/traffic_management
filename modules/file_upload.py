import base64

import streamlit as st

from services import upload_file_to_backend


def render_upload():
    st.header("📁 Upload for AI Violation Analysis")
    st.caption("Upload a road image or recorded footage to check for helmet, seatbelt and licence plate violations.")

    uploaded_file = st.file_uploader(
        "Choose an image or video",
        type=["jpg", "jpeg", "png", "mp4", "avi", "mov"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        if uploaded_file.type and uploaded_file.type.startswith("image"):
            st.image(uploaded_file, caption="Uploaded input", use_container_width=True)
        else:
            st.video(uploaded_file)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.info(f"File: {uploaded_file.name}")
            st.info(f"Size: {uploaded_file.size / (1024 * 1024):.2f} MB")

        with col_b:
            if st.button("Analyze Violations", type="primary"):
                with st.spinner("Running YOLO violation detection..."):
                    result = upload_file_to_backend(uploaded_file)

                if result.get("status") == "success":
                    st.success("Detection completed successfully.")
                    st.balloons()

                    annotated_image = base64.b64decode(result.get("image_b64", ""))
                    if annotated_image:
                        st.image(annotated_image, caption="Annotated detection output", use_container_width=True)

                    class_counts = result.get("class_counts", {})
                    violations = result.get("violations", [])

                    metric_cols = st.columns(4)
                    metric_cols[0].metric("Without Helmet", class_counts.get("without_helmet", 0))
                    metric_cols[1].metric("No Seatbelt", class_counts.get("no_seatbelt", 0))
                    metric_cols[2].metric("Licence Plates", class_counts.get("licence_plate", 0))
                    metric_cols[3].metric("Detected Violations", len(violations))

                    if violations:
                        st.error(
                            "Detected: " + ", ".join(v.replace("_", " ").title() for v in violations)
                        )
                    else:
                        st.success("No violation detected in this frame.")
                else:
                    st.error(result.get("error", "Analysis failed."))
    else:
        st.info("Upload a traffic image or a short video clip to process it with the AI model.")
