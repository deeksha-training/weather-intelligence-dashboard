import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            print(f"[ERROR] Weather failed for {city}: {data.get('message')}")
            return None

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather": data["weather"][0]["description"]
        }

    except Exception as e:
        print(f"[ERROR] Weather failed for {city}: {e}")
        return None


def get_aqi(lat, lon):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=european_aqi,pm10,pm2_5"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        return {
            "aqi": data["hourly"]["european_aqi"][0],
            "pm10": data["hourly"]["pm10"][0],
            "pm25": data["hourly"]["pm2_5"][0]
        }

    except Exception as e:
        print(f"[ERROR] AQI failed: {e}")
        return None


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="weather_app",
        user="weather_user",
        password="weather_pass"
    )


def insert_city_if_not_exists(weather):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO weather_app.cities
        (name, country, latitude, longitude)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name, country)
        DO NOTHING;
    """, (
        weather["city"],
        weather["country"],
        weather["lat"],
        weather["lon"]
    ))

    conn.commit()

    cur.close()
    conn.close()


def insert_readings(city_name, weather, aqi):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM weather_app.cities
        WHERE name = %s
    """, (city_name,))

    city_row = cur.fetchone()

    if city_row is None:
        print(f"[ERROR] City not found in DB: {city_name}")
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


city_name = input("Enter city name: ")

weather = get_weather(city_name)

if weather:
    aqi = get_aqi(weather["lat"], weather["lon"])

    if aqi:
        insert_city_if_not_exists(weather)
        insert_readings(weather["city"], weather, aqi)

        print(
            f"[OK] inserted weather + AQI for {weather['city']}, "
            f"{weather['country']}"
        )