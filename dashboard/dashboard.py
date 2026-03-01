import streamlit as st
import pandas as pd
from pyhive import hive
import pydeck as pdk
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
               event_timestamp,
               temperature,
               humidity,
               wind_speed,
               alert,
               predicted_event,
               risk_level,
               confidence,
               lat,
               lon
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
# Apply Filters
# ------------------------------

if not df.empty:
    df = df[df["risk_level"].isin(risk_filter)]
    df = df[df["confidence"] >= confidence_threshold]
    df = df.dropna(subset=["lat", "lon"])

# ------------------------------
# Map Section
# ------------------------------

st.subheader("🌍 City Risk Heatmap")

if df.empty:
    st.warning("No data matching selected filters.")
else:

    # ------------------------------
    # Hardcoded City Coordinates
    # ------------------------------

    CITY_COORDS = {
        "Bangalore": {"lat": 12.97, "lon": 77.59},
        "New York": {"lat": 40.71, "lon": -74.00},
        "Paris": {"lat": 48.85, "lon": 2.35}
    }

    selected_city = st.selectbox(
        "Select City",
        list(CITY_COORDS.keys())
    )

    city_lat = CITY_COORDS[selected_city]["lat"]
    city_lon = CITY_COORDS[selected_city]["lon"]

    # ------------------------------
    # Filter Sensors Near City
    # ------------------------------

    radius = 0.6  # degrees (~60km)

    city_df = df[
        (df["lat"].between(city_lat - radius, city_lat + radius)) &
        (df["lon"].between(city_lon - radius, city_lon + radius))
    ]

    if city_df.empty:
        st.warning("No alerts currently in this city.")
    else:

        # ------------------------------
        # Heatmap
        # ------------------------------

        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=city_df,
            get_position='[lon, lat]',
            get_weight="confidence",
            radiusPixels=60,
        )

        view_state = pdk.ViewState(
            latitude=city_lat,
            longitude=city_lon,
            zoom=9,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[heatmap_layer],
            initial_view_state=view_state,
        ))

        # ------------------------------
        # City Alert Panel
        # ------------------------------

        st.divider()
        st.subheader(f"📍 {selected_city} Risk Summary")

        top_alert = city_df.sort_values("confidence", ascending=False).iloc[0]

        risk = top_alert["risk_level"]
        alert_text = top_alert["alert"]
        confidence = top_alert["confidence"]

        if risk == "HIGH":
            st.error(f"🚨 HIGH RISK\n\n{alert_text}\n\nConfidence: {confidence}")
        elif risk == "MEDIUM":
            st.warning(f"⚠ MEDIUM RISK\n\n{alert_text}\n\nConfidence: {confidence}")
        else:
            st.success(f"✅ LOW RISK\n\n{alert_text}\n\nConfidence: {confidence}")

    # ------------------------------
    # Location Selection Panel
    # ------------------------------

    st.divider()
    st.subheader("📍 Location Alert Panel")

    df["location_label"] = (
        df["lat"].round(2).astype(str) + ", " +
        df["lon"].round(2).astype(str)
    )

    selected_location = st.selectbox(
        "Select a Location",
        df["location_label"].unique()
    )

    selected_row = df[df["location_label"] == selected_location].iloc[0]

    risk = selected_row["risk_level"]
    alert_text = selected_row["alert"]
    confidence = selected_row["confidence"]

    if risk == "HIGH":
        st.error(f"🚨 HIGH RISK\n\n{alert_text}\n\nConfidence: {confidence}")
    elif risk == "MEDIUM":
        st.warning(f"⚠ MEDIUM RISK\n\n{alert_text}\n\nConfidence: {confidence}")
    else:
        st.success(f"✅ LOW RISK\n\n{alert_text}\n\nConfidence: {confidence}")

    # ------------------------------
    # Metrics & Charts
    # ------------------------------

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Records", len(df))
    col2.metric("High Risk Alerts",
                len(df[df["risk_level"] == "HIGH"]))
    col3.metric("Medium Risk Alerts",
                len(df[df["risk_level"] == "MEDIUM"]))
    col4.metric("Avg AI Confidence",
                round(df["confidence"].mean(), 2))

    st.subheader("📈 Temperature Trend")
    st.line_chart(df["temperature"])

    st.subheader("🚨 Risk Distribution")
    st.bar_chart(df["risk_level"].value_counts())

    st.subheader("🌪 Event Distribution")
    st.bar_chart(df["predicted_event"].value_counts())

# ------------------------------
# Auto Refresh
# ------------------------------

if auto_refresh:
    time.sleep(5)
    st.rerun()