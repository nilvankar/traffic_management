import streamlit as st


def render_support():
    st.header("🛠️ Support Center")
    st.caption("Operational help and guidance for traffic enforcement dashboard users.")

    tab_contact, tab_faq, tab_system = st.tabs(["Contact Support", "FAQ", "System Info"])

    with tab_contact:
        st.subheader("Report an issue")
        with st.form("support_form"):
            issue_type = st.selectbox("Issue Type", ["Camera Offline", "Login Issue", "False Detection", "System Error", "Other"])
            description = st.text_area("Description", placeholder="Describe the problem in detail...")
            submitted = st.form_submit_button("Submit Ticket")
            if submitted:
                st.success("Support ticket created successfully. The operations team will review it shortly.")

    with tab_faq:
        st.subheader("Frequently Asked Questions")

        with st.expander("How do I add a new camera stream?"):
            st.write("Register the new RTSP or local stream through the backend configuration and restart the detection service.")

        with st.expander("Where are violations saved?"):
            st.write("The backend stores every analyzed image and violation record in SQLite, including timestamps and saved result images.")

        with st.expander("What detection classes are supported?"):
            st.write("The current model supports helmet violations, seatbelt violations, licence plate detection and general vehicle recognition.")

    with tab_system:
        st.subheader("System Overview")
        st.markdown(
            """
            - Model: YOLO-based traffic safety detection
            - Database: SQLite 3
            - Backend: Flask API
            - Frontend: Streamlit dashboard
            - Output storage: /backend/outputs and /backend/uploads
            """
        )
