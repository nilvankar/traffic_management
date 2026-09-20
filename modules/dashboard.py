import pandas as pd
import streamlit as st

from services import get_dashboard_stats, get_recent_violations


def render_dashboard():
    st.header("🚦 Traffic Intelligence Center")
    st.caption("Multi-violation detection dashboard for helmet, seatbelt, plate and safety compliance events.")

    stats = get_dashboard_stats()

    top_cards = st.columns(4)
    top_cards[0].metric("Total Violations", stats.get("total_violations", 0), "Live")
    top_cards[1].metric("Today", stats.get("today_violations", 0), "Updated")
    top_cards[2].metric("Helmet Violations", stats.get("helmet_violations", 0), "AI flagged")
    top_cards[3].metric("Seatbelt Violations", stats.get("seatbelt_violations", 0), "AI flagged")

    st.divider()

    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.subheader("📍 Live Camera Overview")
        st.image(
            "https://images.unsplash.com/photo-1566835848608-89c030d97274?q=80&w=1000&auto=format&fit=crop",
            caption="Camera Feed • MG Road Junction",
            use_container_width=True,
        )

        st.subheader("📊 Violation Distribution")
        recent_df = get_recent_violations()
        if not recent_df.empty:
            counts = recent_df["violation_type"].str.replace("_", " ").value_counts()
            chart_df = pd.DataFrame({"Violation": counts.index, "Count": counts.values})
            st.bar_chart(chart_df.set_index("Violation"), use_container_width=True)
        else:
            st.info("No violation records have been logged yet.")

    with right_col:
        st.subheader("🔔 Recent Alerts")
        recent_df = get_recent_violations()

        if recent_df.empty:
            st.info("No recent alerts.")
        else:
            for _, row in recent_df.head(6).iterrows():
                with st.container():
                    badge = "⚠️" if row.get("status") == "Pending" else "✅"
                    st.markdown(
                        f"<div style='padding:0.8rem 1rem;border:1px solid rgba(148,163,184,.2);border-radius:12px;background:rgba(15,23,42,.75);margin-bottom:0.6rem;'>"
                        f"<strong>{badge} {row.get('violation_type', 'Violation')}</strong><br>"
                        f"<small>{row.get('location', 'Unknown location')}</small><br>"
                        f"<small>{row.get('timestamp', 'Unknown time')} • {row.get('status', 'Pending')}</small>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    st.divider()

    st.subheader("🗂️ Recent Violations Table")
    recent_df = get_recent_violations()
    if recent_df.empty:
        st.info("No records available in the database.")
    else:
        display_df = recent_df[[
            "timestamp",
            "violation_type",
            "location",
            "status",
            "source",
        ]].copy()
        display_df.columns = ["Time", "Violation Type", "Location", "Status", "Source"]
        st.dataframe(display_df.head(12), use_container_width=True, hide_index=True)

