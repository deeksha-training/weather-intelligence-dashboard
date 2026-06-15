import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.title("🌦 City Weather Intelligence Dashboard")


data = requests.get("http://127.0.0.1:8000/weather").json()
df = pd.DataFrame(data)

cities = df["city"].unique()

selected_cities = st.sidebar.multiselect(
    "Select cities",
    cities,
    default=cities
)

filtered_df = df[df["city"].isin(selected_cities)]

if filtered_df.empty:
    st.warning("No data available for selected cities.")
else:
    avg_temp = filtered_df["temp_celsius"].mean()
    avg_aqi = filtered_df["aqi"].mean()
    highest_humidity_city = filtered_df.sort_values("humidity_pct", ascending=False).iloc[0]["city"]
    windiest_city = filtered_df.sort_values("wind_speed_mps", ascending=False).iloc[0]["city"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Temp °C", round(avg_temp, 2))
    col2.metric("Avg AQI", round(avg_aqi, 2))
    col3.metric("Highest Humidity", highest_humidity_city)
    col4.metric("Windiest City", windiest_city)

    st.subheader("Temperature by City")
    fig = px.bar(filtered_df, x="city", y="temp_celsius")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("AQI by City")
    fig2 = px.bar(filtered_df, x="city", y="aqi")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Humidity vs AQI")
    fig3 = px.scatter(filtered_df, x="humidity_pct", y="aqi", color="city")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Data")
    st.dataframe(filtered_df)

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        "filtered_weather_data.csv",
        "text/csv"
    )