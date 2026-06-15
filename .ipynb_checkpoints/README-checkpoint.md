# Weather Intelligence Dashboard

## Overview

A weather analytics dashboard built using:

- OpenWeather API
- Open Meteo AQI API
- PostgreSQL
- FastAPI
- Pandas
- Streamlit

## Architecture

Weather API + AQI API
        ↓
    collect.py
        ↓
    PostgreSQL
        ↓
      FastAPI
        ↓
    Streamlit

## Features

- Weather collection for 10 cities
- Air Quality Index tracking
- PostgreSQL storage
- ETL processing with Pandas
- FastAPI backend
- Interactive Streamlit dashboard

## Run

### Database

```bash
docker start weather_db
```

### Collect Data

```bash
python collect.py
```

### API

```bash
uvicorn api:app --reload
```

### Dashboard

```bash
streamlit run app.py
```