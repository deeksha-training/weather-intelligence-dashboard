import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://weather_user:weather_pass@localhost:5432/weather_app"
)

query = """
SELECT
    c.name AS city,
    w.recorded_at,
    w.temp_celsius,
    w.humidity_pct,
    w.wind_speed_mps,
    w.weather_desc,
    a.aqi,
    a.pm25,
    a.pm10
FROM weather_app.weather_readings w
JOIN weather_app.cities c
ON c.id = w.city_id
LEFT JOIN weather_app.aqi_readings a
ON c.id = a.city_id
AND w.recorded_at = a.recorded_at
ORDER BY w.recorded_at DESC;
"""

df = pd.read_sql(query, engine)

df = (
    df.sort_values("recorded_at", ascending=False)
      .drop_duplicates(subset=["city"], keep="first")
)

df["temp_fahrenheit"] = (df["temp_celsius"] * 9/5) + 32
df["wind_speed_kph"] = df["wind_speed_mps"] * 3.6
df["heat_index"] = df["temp_celsius"] + (0.33 * df["humidity_pct"]) - 4


def get_aqi_category(aqi):
    if pd.isna(aqi):
        return "Unknown"
    elif aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive"
    else:
        return "Unhealthy"


def get_time_of_day(hour):
    if 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 17:
        return "Afternoon"
    elif 18 <= hour <= 23:
        return "Evening"
    else:
        return "Night"


df["aqi_category"] = df["aqi"].apply(get_aqi_category)
df["time_of_day"] = df["recorded_at"].dt.hour.apply(get_time_of_day)

df.to_csv("clean_weather_data.csv", index=False)

print("Clean weather data saved to clean_weather_data.csv")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")