import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="WeatherWise", page_icon="🌦", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.2rem; }

.hero {
    background: linear-gradient(135deg, #dbeafe, #f5d0fe);
    padding: 30px;
    border-radius: 24px;
    margin-bottom: 22px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
}

.hero-subtitle {
    font-size: 16px;
    color: #374151;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid #eef1f6;
}

.metric-label {
    font-size: 14px;
    color: #6b7280;
}

.metric-value {
    font-size: 34px;
    font-weight: 800;
    color: #111827;
}
</style>
""", unsafe_allow_html=True)


def weather_icon(desc):
    desc = str(desc).lower()

    if "clear" in desc:
        return "☀️"
    if "cloud" in desc:
        return "⛅"
    if "rain" in desc:
        return "🌧"
    if "storm" in desc:
        return "⛈"
    if "snow" in desc:
        return "❄️"

    return "🌦"

def weather_code_icon(code):
    if code == 0:
        return "☀️"
    elif code in [1, 2]:
        return "🌤️"
    elif code == 3:
        return "☁️"
    elif code in [45, 48]:
        return "🌫️"
    elif code in [51, 53, 55, 56, 57]:
        return "🌦️"
    elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "🌧️"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "❄️"
    elif code in [95, 96, 99]:
        return "⛈️"
    else:
        return "🌦️"


def aqi_category(aqi):
    if pd.isna(aqi):
        return "Unknown"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive"
    return "Unhealthy"


def aqi_color(aqi):
    if pd.isna(aqi):
        return "#9ca3af"
    if aqi <= 50:
        return "#22c55e"
    if aqi <= 100:
        return "#f59e0b"
    return "#ef4444"


def get_live_weather(city):
    response = requests.get(f"{API_BASE_URL}/live-weather/{city}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_forecast(city):
    response = requests.get(f"{API_BASE_URL}/forecast/{city}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_history(city):
    try:
        response = requests.get(f"{API_BASE_URL}/history/{city}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ----------------------------
# Sidebar inputs
# ----------------------------
st.sidebar.title("🌦 WeatherWise")
st.sidebar.caption("Search-based Weather Intelligence")

city = st.sidebar.text_input(
    "Search city",
    value="New York",
    placeholder="Enter city name and press Enter"
)

report_type = st.sidebar.radio(
    "Report type",
    ["Current", "Hourly", "Daily"]
)

unit = st.sidebar.radio(
    "Temperature unit",
    ["Celsius", "Fahrenheit"],
    horizontal=True
)


if not city.strip():
    st.info("Enter a city name from the left panel.")
    st.stop()


# ----------------------------
# Fetch data
# ----------------------------
try:
    current = get_live_weather(city)
    forecast = get_forecast(city)
except Exception as e:
    st.error("Could not fetch weather.")
    st.exception(e)
    st.stop()

if "error" in current:
    st.error(current["error"])
    st.stop()

history_df = get_history(current["city"])


# ----------------------------
# Prepare current data
# ----------------------------
current["temp_fahrenheit"] = (current["temp_celsius"] * 9 / 5) + 32
current["wind_speed_kph"] = current["wind_speed_mps"] * 3.6
current["heat_index"] = current["temp_celsius"] + (0.33 * current["humidity_pct"]) - 4
current["aqi_category"] = aqi_category(current["aqi"])

display_temp = current["temp_celsius"] if unit == "Celsius" else current["temp_fahrenheit"]
temp_symbol = "°C" if unit == "Celsius" else "°F"


# ---------------------------

# ----------------------------
# Hero
# ----------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-subtitle">Weather intelligence report for</div>
    <div class="hero-title">
        {current["city"]}, {current["country"]} {weather_icon(current["weather_desc"])}
    </div>
    <div class="hero-subtitle">{current["recorded_at"]}</div>
</div>
""", unsafe_allow_html=True)


# ----------------------------
# Summary cards
# ----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Temperature</div>
        <div class="metric-value">{display_temp:.1f}{temp_symbol}</div>
        <div>{str(current["weather_desc"]).title()}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Humidity</div>
        <div class="metric-value">{current["humidity_pct"]}%</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Wind Speed</div>
        <div class="metric-value">{current["wind_speed_kph"]:.1f}</div>
        <div>km/h</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">AQI</div>
        <div class="metric-value">{current["aqi"]}</div>
        <div>{current["aqi_category"]}</div>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------
# AQI gauge
# ----------------------------
st.markdown("### Air Quality Overview")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=current["aqi"],
    title={"text": f"AQI - {current['aqi_category']}"},
    gauge={
        "axis": {"range": [0, 200]},
        "bar": {"color": aqi_color(current["aqi"])},
        "steps": [
            {"range": [0, 50], "color": "#dcfce7"},
            {"range": [51, 100], "color": "#fef3c7"},
            {"range": [101, 200], "color": "#fee2e2"},
        ],
    }
))

fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# Hourly report
# ----------------------------
# ----------------------------
# Hourly report
# ----------------------------
if report_type == "Hourly":
    st.markdown("### Today's Outlook")
    st.subheader("Every 1-hour forecast for today")

    hourly = pd.DataFrame(forecast.get("hourly", []))

    if hourly.empty:
        st.warning("No hourly forecast data available.")
    else:
        hourly["time"] = pd.to_datetime(hourly["time"])
        hourly["date"] = hourly["time"].dt.date
        hourly["hour"] = hourly["time"].dt.strftime("%I %p")

        # use the first forecast date from API instead of laptop date
        selected_date = hourly["date"].min()

        today_df = hourly[hourly["date"] == selected_date].copy()

        if today_df.empty:
            st.warning("No hourly data available for today.")
        else:
            today_df = today_df.head(24)

            st.markdown("#### Hour-by-hour")

            cols = st.columns(6)

            for i, (_, row) in enumerate(today_df.iterrows()):
                with cols[i % 6]:
                    icon = weather_code_icon(row["weather_code"]) if "weather_code" in row else "🌦"

                    label = "Now" if i == 0 else row["hour"]

                    st.markdown(
                        f"""
                        <div class="card" style="text-align:center; min-height:165px; margin-bottom:16px;">
                            <div style="font-weight:700; font-size:14px;">{label}</div>
                            <div style="font-size:34px; margin-top:10px;">{icon}</div>
                            <div style="font-size:28px; font-weight:800; margin-top:10px;">
                                {row["temperature_2m"]:.0f}°
                            </div>
                            <div style="font-size:12px; color:#6b7280;">
                                Rain {row["precipitation_probability"]}%
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            fig = px.line(
                today_df,
                x="hour",
                y="temperature_2m",
                markers=True,
                title="Today's Temperature Trend"
            )

            fig.update_traces(line=dict(width=4))
            fig.update_layout(
                xaxis_title="Hour",
                yaxis_title="Temperature °C",
                height=420
            )

            st.plotly_chart(fig, use_container_width=True)
            
# ----------------------------
# Daily report
# ----------------------------
elif report_type == "Daily":
    st.markdown("### 7-Day Daily Forecast")

    daily = pd.DataFrame(forecast.get("daily", []))

    if daily.empty:
        st.warning("No daily forecast data available.")
    else:
        daily["time"] = pd.to_datetime(daily["time"]).dt.strftime("%a, %b %d")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=daily["time"],
            y=daily["temperature_2m_max"],
            mode="lines+markers",
            name="Max Temp"
        ))

        fig.add_trace(go.Scatter(
            x=daily["time"],
            y=daily["temperature_2m_min"],
            mode="lines+markers",
            name="Min Temp"
        ))

        fig.update_layout(
            title="Daily Temperature Forecast",
            xaxis_title="Day",
            yaxis_title="Temperature °C",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(daily, use_container_width=True)


# ----------------------------
# # Monthly report
# # ----------------------------
# elif report_type == "Monthly":
#     st.markdown("### Monthly Historical Report")

#     if history_df.empty:
#         st.warning("No saved historical data found for this city yet.")
#     else:
#         history_df["recorded_at"] = pd.to_datetime(history_df["recorded_at"])
#         history_df["month"] = history_df["recorded_at"].dt.to_period("M").astype(str)

#         monthly = history_df.groupby("month").agg(
#             avg_temp=("temp_celsius", "mean"),
#             avg_humidity=("humidity_pct", "mean"),
#             avg_aqi=("aqi", "mean"),
#             readings=("city", "count")
#         ).reset_index()

#         fig = px.line(
#             monthly,
#             x="month",
#             y="avg_temp",
#             markers=True,
#             title="Monthly Average Temperature"
#         )

#         fig.update_layout(
#             xaxis_title="Month",
#             yaxis_title="Average Temperature °C",
#             height=450
#         )

#         st.plotly_chart(fig, use_container_width=True)
#         st.dataframe(monthly, use_container_width=True)

#         st.caption(
#             "Monthly report uses only saved PostgreSQL data. "
#             "Collect more data over time to make this meaningful."
#         )


# ----------------------------
# Current report
# ----------------------------
else:
    st.markdown("### Current Weather Recommendation")

    if current["aqi"] <= 50:
        st.success("Air quality is good. Great time for outdoor activities.")
    elif current["aqi"] <= 100:
        st.warning("Air quality is moderate. Sensitive people should limit prolonged outdoor activity.")
    else:
        st.error("Air quality is poor. Avoid heavy outdoor activity if possible.")

    st.markdown("### Weather Summary")

    st.info(
        f"""
        Current conditions in {current['city']}:

        • Temperature: {display_temp:.1f}{temp_symbol}  
        • Humidity: {current['humidity_pct']}%  
        • Wind Speed: {current['wind_speed_kph']:.1f} km/h  
        • Air Quality: {current['aqi_category']}
        """
    )