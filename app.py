import streamlit as st

from modules.dashboard import render_dashboard
from modules.file_upload import render_upload
from modules.login import render_login
from modules.support import render_support

st.set_page_config(
    page_title="Traffic Sentinel AI",
    page_icon="🚦",
    layout="wide",
)

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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login()
else:
    with st.sidebar:
        st.image(
            "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=200&q=80",
            use_container_width=True,
        )
        st.title("Traffic Sentinel")
        st.caption(f"Operator: {st.session_state.get('username', 'Admin')}")

        page = st.radio(
            "Navigation",
            ["Dashboard", "Upload", "Support"],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.pop("username", None)
            st.rerun()

    if page == "Dashboard":
        render_dashboard()
    elif page == "Upload":
        render_upload()
    else:
        render_support()
