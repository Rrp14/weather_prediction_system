import streamlit as st
import pandas as pd
from pyhive import hive
import time

st.set_page_config(layout="wide")
st.title("🌍 Climate Monitoring & AI Risk Platform")

# ------------------------------
# Sidebar Controls
# ------------------------------

st.sidebar.header("⚙ Controls")

risk_filter = st.sidebar.multiselect(
    "Filter Risk Level",
    ["HIGH", "MEDIUM", "LOW"],
    default=["HIGH", "MEDIUM", "LOW"]
)

confidence_threshold = st.sidebar.slider(
    "Minimum AI Confidence",
    0.0, 1.0, 0.5
)

limit = st.sidebar.slider(
    "Records to Fetch",
    100, 5000, 1000
)

auto_refresh = st.sidebar.checkbox("Auto Refresh (5 sec)")

# ------------------------------
# Load Data
# ------------------------------

@st.cache_data(ttl=5)
def load_data(limit):
    try:
        conn = hive.Connection(
            host='localhost',
            port=10000,
            username='rrp',
            auth='NOSASL'
        )

        query = f"""
        SELECT sensor_id_hash,
               temperature,
               humidity,
               wind_speed,
               alert,
               predicted_event,
               risk_level,
               confidence
        FROM climate_predictions
        LIMIT {limit}
        """

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    except Exception as e:
        st.error(f"Hive error: {e}")
        return pd.DataFrame()

df = load_data(limit)

# ------------------------------
# Filter Data
# ------------------------------

if not df.empty:
    df = df[df["risk_level"].isin(risk_filter)]
    df = df[df["confidence"] >= confidence_threshold]

# ------------------------------
# Dashboard
# ------------------------------

if df.empty:
    st.warning("No data matching selected filters...")
else:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Records", len(df))
    col2.metric("High Risk Alerts",
                len(df[df["risk_level"] == "HIGH"]))
    col3.metric("Medium Risk Alerts",
                len(df[df["risk_level"] == "MEDIUM"]))
    col4.metric("Avg AI Confidence",
                round(df["confidence"].mean(), 2))

    st.divider()

    st.subheader("📈 Temperature Trend")
    st.line_chart(df["temperature"])

    st.subheader("🧠 AI Confidence Trend")
    st.line_chart(df["confidence"])

    st.subheader("🚨 Risk Distribution")
    st.bar_chart(df["risk_level"].value_counts())

    st.subheader("🌪 Event Distribution")
    st.bar_chart(df["predicted_event"].value_counts())

    st.subheader("🌐 Sample Multilingual Alerts")
    st.dataframe(
        df[["alert", "predicted_event", "risk_level", "confidence"]]
        .sort_values("confidence", ascending=False)
        .head(20)
    )

# ------------------------------
# Auto Refresh
# ------------------------------

if auto_refresh:
    time.sleep(5)
    st.rerun()