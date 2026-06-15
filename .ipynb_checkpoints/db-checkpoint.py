import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="weather_app",
    user="weather_user",
    password="weather_pass"
)

cur = conn.cursor()

cur.execute("""
CREATE SCHEMA IF NOT EXISTS weather_app;

CREATE TABLE IF NOT EXISTS weather_app.cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    country VARCHAR(10),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6)
);
""")

cities = [
    ("New York", "US", 40.7128, -74.0060),
    ("London", "GB", 51.5074, -0.1278),
    ("Tokyo", "JP", 35.6762, 139.6503),
    ("Sydney", "AU", -33.8688, 151.2093),
    ("Paris", "FR", 48.8566, 2.3522),
    ("Mumbai", "IN", 19.0760, 72.8777),
    ("Toronto", "CA", 43.6532, -79.3832),
    ("Dubai", "AE", 25.2048, 55.2708),
    ("Berlin", "DE", 52.5200, 13.4050),
    ("São Paulo", "BR", -23.5505, -46.6333)
]

for city in cities:
 cur.execute("""
    INSERT INTO weather_app.cities
    (name, country, latitude, longitude)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name, country)
    DO NOTHING
""", city)

conn.commit()

print("Cities inserted successfully!")

cur.close()
conn.close()