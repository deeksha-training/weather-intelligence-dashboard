import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url, timeout=10)
    data = response.json()

    if response.status_code != 200:
        print(f"[ERROR] Weather failed for {city}")
        return None

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "weather": data["weather"][0]["description"]
    }


def get_aqi(lat, lon):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=european_aqi,pm10,pm2_5"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    return {
        "aqi": data["hourly"]["european_aqi"][0],
        "pm10": data["hourly"]["pm10"][0],
        "pm25": data["hourly"]["pm2_5"][0]
    }


def insert_readings(city_name, weather, aqi):
    conn = psycopg2.connect(
        host="localhost",
        database="weather_app",
        user="weather_user",
        password="weather_pass"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM weather_app.cities
        WHERE name = %s
    """, (city_name,))

    city_row = cur.fetchone()

    if city_row is None:
        print(f"City not found in DB: {city_name}")
        cur.close()
        conn.close()
        return

    city_id = city_row[0]
    recorded_at = datetime.now()

    cur.execute("""
        INSERT INTO weather_app.weather_readings
        (city_id, recorded_at, temp_celsius, humidity_pct, wind_speed_mps, weather_desc)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        city_id,
        recorded_at,
        weather["temperature"],
        weather["humidity"],
        weather["wind_speed"],
        weather["weather"]
    ))

    cur.execute("""
        INSERT INTO weather_app.aqi_readings
        (city_id, recorded_at, aqi, pm25, pm10)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        city_id,
        recorded_at,
        aqi["aqi"],
        aqi["pm25"],
        aqi["pm10"]
    ))

    conn.commit()
    cur.close()
    conn.close()


cities = [
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832},
    {"name": "Dubai", "lat": 25.2048, "lon": 55.2708},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333}
]


for city in cities:
    weather = get_weather(city["name"])
    aqi = get_aqi(city["lat"], city["lon"])

    if weather and aqi:
        insert_readings(city["name"], weather, aqi)
        print(f"[OK] inserted weather + AQI for {city['name']}")