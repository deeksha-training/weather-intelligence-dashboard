from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
API_KEY = os.getenv("WEATHER_API_KEY")

engine = create_engine(
    "postgresql+psycopg2://weather_user:weather_pass@localhost:5432/weather_app"
)


@app.get("/")
def home():
    return {"message": "Weather API Running"}


def clean_records(df):
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def get_city_coordinates(city_name):
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if response.status_code != 200:
        return None

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
        "temp_celsius": data["main"]["temp"],
        "humidity_pct": data["main"]["humidity"],
        "wind_speed_mps": data["wind"]["speed"],
        "weather_desc": data["weather"][0]["description"],
        "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@app.get("/live-weather/{city_name}")
def live_weather(city_name: str):
    city_data = get_city_coordinates(city_name)

    if city_data is None:
        return {"error": f"City not found: {city_name}"}

    aqi_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={city_data['lat']}&longitude={city_data['lon']}"
        "&hourly=european_aqi,pm10,pm2_5"
    )

    aqi_response = requests.get(aqi_url, timeout=10)
    aqi_data = aqi_response.json()

    city_data["aqi"] = aqi_data["hourly"]["european_aqi"][0]
    city_data["pm25"] = aqi_data["hourly"]["pm2_5"][0]
    city_data["pm10"] = aqi_data["hourly"]["pm10"][0]

    return city_data


@app.get("/forecast/{city_name}")
def forecast(city_name: str):
    city_data = get_city_coordinates(city_name)

    if city_data is None:
        return {"error": f"City not found: {city_name}"}

    url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={city_data['lat']}&longitude={city_data['lon']}"
    "&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m,weather_code"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code"
    "&timezone=auto"
    "&forecast_days=10"
)

    response = requests.get(url, timeout=10)
    data = response.json()

    return {
        "city": city_data["city"],
        "country": city_data["country"],
        "hourly": data["hourly"],
        "daily": data["daily"]
    }

@app.get("/history/{city_name}")
def city_history(city_name: str):
    query = """
    SELECT
        c.name AS city,
        c.country,
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
    WHERE LOWER(c.name) = LOWER(%s)
    ORDER BY w.recorded_at DESC
    LIMIT 100;
    """

    try:
        df = pd.read_sql(query, engine, params=(city_name,))

        if df.empty:
            return []

        df["recorded_at"] = df["recorded_at"].astype(str)

        return clean_records(df)

    except Exception as e:
        print("History endpoint error:", e)
        return []