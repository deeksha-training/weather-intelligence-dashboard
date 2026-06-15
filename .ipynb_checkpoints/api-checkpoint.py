from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI()

engine = create_engine(
    "postgresql+psycopg2://weather_user:weather_pass@localhost:5432/weather_app"
)


@app.get("/")
def home():
    return {"message": "Weather API Running"}


@app.get("/weather")
def get_weather_data():

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

    df["recorded_at"] = df["recorded_at"].astype(str)

    records = df.where(pd.notnull(df), None)

    return records.to_dict(orient="records")