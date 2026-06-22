# Weather Intelligence Dashboard - Architecture

## 1. Project Overview

This project is an end-to-end weather intelligence dashboard built using Python.

It allows users to search for a city and view:

- Current weather
- Air Quality Index
- Hourly forecast
- Daily forecast
- Weather recommendations

## 2. High-Level Architecture

```text
User
 ↓
Streamlit Frontend (app.py)
 ↓
FastAPI Backend (api.py)
 ↓
External Weather APIs




## 3. Components
Streamlit Frontend - app.py
The frontend is responsible for displaying the dashboard.
Responsibilities:


City search input


Current weather cards


AQI gauge


Hourly forecast cards


Daily forecast charts


User-friendly UI


It does not directly call external weather APIs. Instead, it calls FastAPI endpoints.
FastAPI Backend - api.py
FastAPI acts as the backend service layer.
Responsibilities:


Expose REST API endpoints


Fetch live weather data


Fetch forecast data


Fetch historical data from PostgreSQL


Return JSON responses to Streamlit


Important endpoints:
GET /live-weather/{city}GET /forecast/{city}GET /history/{city}
PostgreSQL Database
PostgreSQL stores historical weather and AQI readings.
Tables:
citiesweather_readingsaqi_readings
The database is used when we want to analyze data over time.
Docker
Docker is used to run PostgreSQL locally without manually installing it on the machine.
Benefits:


Easy setup


Isolated database environment


Reproducible development


Persistent storage using Docker volume


collect.py
This script collects weather and AQI data and stores it in PostgreSQL.
It represents the data ingestion pipeline.
db.py
This script creates the required database schema and tables.
4. Data Flow
Live Weather Flow
User searches city ↓Streamlit calls FastAPI ↓FastAPI calls OpenWeather API ↓FastAPI returns JSON ↓Streamlit displays weather cards
Forecast Flow
User selects Hourly or Daily ↓Streamlit calls FastAPI /forecast endpoint ↓FastAPI calls Open-Meteo forecast API ↓FastAPI returns hourly/daily forecast JSON ↓Streamlit renders forecast cards and charts
Historical Flow
collect.py runs ↓Weather data saved into PostgreSQL ↓FastAPI reads saved data through /history ↓Streamlit displays historical analysis
5. Database Design
cities
Stores city metadata.
idnamecountrylatitudelongitude
weather_readings
Stores changing weather measurements.
idcity_idrecorded_attemp_celsiushumidity_pctwind_speed_mpsweather_desc
aqi_readings
Stores air quality data.
idcity_idrecorded_ataqipm25pm10
6. Why Separate Tables?
The database is normalized.
City information is stored once in cities.
Weather readings and AQI readings reference the city using city_id.
This avoids repeating city name, country, latitude and longitude in every reading.
7. Why FastAPI?
FastAPI separates backend logic from the UI.
Instead of Streamlit directly calling external APIs or PostgreSQL, Streamlit calls FastAPI.
Benefits:


Cleaner architecture


API key remains hidden


Backend logic is reusable


Easier to add another frontend later


8. Why Streamlit?
Streamlit is used to quickly build an interactive Python dashboard.
It is responsible only for the user interface.
9. Why PostgreSQL?
PostgreSQL is used to store historical data.
Live data can come directly from APIs, but historical trends require saved records.
10. Why Docker?
Docker runs PostgreSQL in an isolated container.
This avoids manual PostgreSQL installation and makes the setup easier to reproduce.
11. Tech Stack
PythonFastAPIStreamlitPostgreSQLDockerPandasPlotlyRequestsSQLAlchemy
12. Final Architecture Summary
Frontend:app.py - Streamlit dashboardBackend:api.py - FastAPI REST APIDatabase:PostgreSQL in DockerData Collection:collect.pyDatabase Setup:db.py
Save:```textCtrl + OEnterCtrl + X
Then commit:
git add ARCHITECTURE.mdgit commit -m "Add architecture documentation"git push