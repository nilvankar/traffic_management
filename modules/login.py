import streamlit as st

from services import check_login


def render_login():
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            "<h1 style='text-align: center; margin-bottom: 0.2rem;'>🚦 Welcome to Metropolicis</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; color: #94a3b8;'>AI Traffic Enforcement & Violation Monitoring</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style='padding: 1.2rem; border-radius: 18px; background: rgba(15,23,42,0.65); border: 1px solid rgba(148,163,184,0.2); margin: 1.5rem 0;'>
                <div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 0.6rem;'>Secure Operator Access</div>
                <div style='color: #94a3b8;'>Monitoring dashboard for helmet, seatbelt, lane and plate compliance.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input("Username", value="admin", placeholder="admin")
            password = st.text_input("Password", type="password", value="admin", placeholder="admin")
            submitted = st.form_submit_button("Login to Dashboard", use_container_width=True)

            if submitted:
                if check_login(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.success("Login successful. Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
