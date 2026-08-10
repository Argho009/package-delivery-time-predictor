# AI-Based Package Delivery Time Prediction System

> **Project #21** | Python · Flask · XGBoost · Random Forest · Linear Regression · Google Maps API · OpenWeather API · MySQL

A full-stack AI system that predicts package delivery times using real logistics data (43,000+ rows from Kaggle), live traffic conditions (Google Maps Distance Matrix API), and real-time weather display (OpenWeather API).

---

## 🏗️ Architecture

```
frontend/               HTML/CSS/JS dashboard (served by Flask)
backend/
├── app.py              Flask app factory
├── config.py           Environment config
├── data/               Dataset download & processing pipeline
│   ├── download_datasets.py   Kaggle API downloader (5 datasets)
│   ├── process_datasets.py    Clean, normalize, merge → unified CSV
│   └── load_to_db.py          Load unified CSV → MySQL
├── models/
│   ├── train.py        Train XGBoost + Random Forest + Linear Regression
│   ├── predict.py      Inference (singleton model loader)
│   └── saved/          .pkl model files + metrics.json
├── services/
│   ├── maps_service.py         Google Maps Distance Matrix API
│   └── weather_service.py      OpenWeather Current Weather API
├── routes/
│   ├── predict.py      POST /api/predict
│   ├── history.py      GET/POST /api/history
│   └── analytics.py    GET /api/analytics/*
├── database/
│   ├── models.py       SQLAlchemy ORM
│   └── seed.py         Synthetic fallback seeder
└── utils/
    └── feature_engineering.py  Feature encoding
```

---

## 🚀 Setup Guide

### 1. Prerequisites

- **Python 3.10+**
- **MySQL 8.x** running locally
- **Google Maps API key** — [Enable Distance Matrix API](https://console.cloud.google.com/)
- **OpenWeather API key** — [Free tier](https://openweathermap.org/api)
- **Kaggle account** — [kaggle.com](https://www.kaggle.com)

---

### 2. Clone & Install

```bash
cd "i:\1. Projects\1. Group\5"

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Configure Environment

```bash
# Copy template
copy .env.example .env

# Edit .env with your actual values:
# - KAGGLE_USERNAME, KAGGLE_KEY
# - GOOGLE_MAPS_API_KEY
# - OPENWEATHER_API_KEY
# - DB_USER, DB_PASSWORD
```

**Kaggle credentials:**
1. Go to [kaggle.com/settings](https://www.kaggle.com/settings) → API → **Create New Token**
2. This downloads `kaggle.json`
3. Place it at `C:\Users\<you>\.kaggle\kaggle.json`

---

### 4. Create MySQL Database

```sql
-- In MySQL client or Workbench:
CREATE DATABASE delivery_db;
```

Or run the full schema:
```bash
mysql -u root -p delivery_db < schema.sql
```

---

### 5. Data Pipeline (one-time setup)

```bash
cd backend

# Step 1: Download 5 Kaggle datasets (~60,000 rows total)
python -m data.download_datasets

# Step 2: Process, clean & merge into unified_delivery.csv
python -m data.process_datasets

# Step 3: Load into MySQL
python -m data.load_to_db
```

**Datasets downloaded:**
| Dataset | Rows | Key Features |
|---|---|---|
| Amazon Delivery | ~43,632 | distance, traffic, time_taken |
| Logistics & Supply Chain | ~10,000 | congestion, lead_time, ETA deviation |
| Global Superstore | ~10,000 | ship_mode, order→ship days |
| E-Commerce Shipment | ~10,000 | weight, mode, on-time flag |
| Enhanced Superstore | ~9,994 | region, ship_mode, dates |

---

### 6. Train ML Models

```bash
# From backend/ directory:
python -m models.train
```

Trains all 3 models on the unified real dataset:
- **XGBoost** (400 estimators, depth 7)
- **Random Forest** (300 trees, depth 14)
- **Linear Regression** (with StandardScaler)

Outputs: `models/saved/xgboost.pkl`, `random_forest.pkl`, `linear_regression.pkl`, `metrics.json`

---

### 7. Run the App

```bash
# From backend/ directory:
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 📊 ML Features Used

| Feature | Description |
|---|---|
| `distance_km` | Route distance from Google Maps |
| `traffic_duration_min` | Traffic-aware travel time (Google Maps) |
| `traffic_level_enc` | LOW=0, MODERATE=1, HIGH=2, SEVERE=3 |
| `package_weight_kg` | Package weight |
| `package_type_enc` | SMALL=0, MEDIUM=1, LARGE=2, FRAGILE=3, PERISHABLE=4 |
| `priority_enc` | STANDARD=0, EXPRESS=1, OVERNIGHT=2 |
| `shipping_mode_enc` | ROAD=0, AIR=1, RAIL=2, SEA=3 |

> **Note:** Weather is displayed in the UI from OpenWeather API but is NOT used as an ML feature, since real logistics datasets don't include weather data.

---

## 🌐 API Endpoints

### `POST /api/predict`
```json
{
  "origin": "Mumbai",
  "destination": "Pune",
  "package_weight_kg": 5.0,
  "package_type": "MEDIUM",
  "priority": "STANDARD",
  "shipping_mode": "ROAD"
}
```

### `GET /api/history?page=1&per_page=20&traffic=HIGH`
### `POST /api/history`
### `GET /api/analytics/summary`
### `GET /api/analytics/model-comparison`
### `GET /api/analytics/traffic-impact`
### `GET /api/analytics/weather-impact`
### `GET /api/health`

---

## 🔧 Alternative: Skip Kaggle (Synthetic Data)

If you don't have a Kaggle account, use the synthetic seeder:

## 🚀 Quick Start (Single Command)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the entire project (auto-prepares models & opens browser)
python main.py
```

---

## 📁 Project Structure

```
5/
├── requirements.txt
├── schema.sql
├── .env.example
├── README.md
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── data/
│   │   ├── raw/                  (gitignored, created by download)
│   │   ├── processed/            (gitignored, created by process)
│   │   ├── download_datasets.py
│   │   ├── process_datasets.py
│   │   └── load_to_db.py
│   ├── models/
│   │   ├── saved/                (gitignored, created by train)
│   │   ├── train.py
│   │   └── predict.py
│   ├── services/
│   │   ├── maps_service.py
│   │   └── weather_service.py
│   ├── routes/
│   │   ├── predict.py
│   │   ├── history.py
│   │   └── analytics.py
│   ├── database/
│   │   ├── db.py
│   │   ├── models.py
│   │   └── seed.py
│   └── utils/
│       └── feature_engineering.py
└── frontend/
    ├── index.html
    ├── predict.html
    ├── history.html
    ├── css/style.css
    └── js/
        ├── main.js
        ├── predict.js
        ├── history.js
        └── charts.js
```
