---
title: DeliverAI Package Delivery Time Predictor
emoji: 🚚
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# AI-Based Package Delivery Time Prediction System

> **DeliverAI** | Python · Flask · 19 ML & Deep Learning Models (Voting, Stacking, Random Forest, Extra Trees, CatBoost, LightGBM, Bagging, HistGradientBoosting, Gradient Boosting, XGBoost, MLP, TabNet, Decision Tree, SVR, KNN, Elastic Net, Ridge, Linear, Lasso) · OSRM & OpenStreetMap · OpenWeather API · SQLite / MySQL

A full-stack AI system that predicts inland India package delivery times using 184,000+ real logistics records (Delhivery, Amazon India, Food Delivery Trips, Bangalore City Traffic, Indian Road Corridors & Accidents, Indian Railway Stations, Flipkart), live traffic simulation, weather delay factors, and 19 Machine Learning & Deep Learning regression models.


---

## 🏗️ Architecture

```
frontend/               HTML/CSS/JS dashboard (served by Flask)
backend/
├── app.py              Flask app factory
├── config.py           Environment config (SQLite / MySQL)
├── data/               Dataset download & processing pipeline
│   ├── download_datasets.py   Kaggle API downloader
│   ├── process_datasets.py    Clean, normalize, merge → 99,500 rows unified CSV
│   └── load_to_db.py          Load unified CSV → Database
├── models/
│   ├── train.py        Train 16 ML & Deep Learning models + Stacking
│   ├── tabnet_model.py TabNet PyTorch estimator wrapper
│   ├── predict.py      Inference (singleton model loader & ensemble predictor)
│   └── saved/          .pkl model files + metrics.json
├── services/
│   ├── maps_service.py         OSRM Routing & Nominatim Geocoding
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

**Inland India Datasets Incorporated (184,000+ Records Total):**
| Dataset / Source | Rows | Key Features & Domain |
|---|---|---|
| **Delhivery Logistics Dataset** | 55,000 | 144k+ real Indian courier routes, OSRM distance, FTL vs Carting, congestion factor |
| **Amazon India Sales & Shipping** | 25,000 | Real Indian e-commerce fulfillment, expedited vs standard, apparel & retail |
| **Hyperlocal Food & Parcel Trips** | 45,593 | Urban two-wheeler routes (Zomato/Swiggy), high traffic sensitivity, rapid ETA |
| **Bangalore City Traffic Corridors** | 8,936 | Real-time Indian metro intersection congestion, peak hour bottlenecks |
| **Indian Road Corridors & Hazards** | 20,000 | NH/SH highway condition factors, weather-sensitive corridors |
| **Indian Railways Freight & Cargo** | 10,000 | Heavy container rail corridors, yard marshaling buffer, DFC track routing |
| **Flipkart E-Commerce Orders** | 1,500 | Multi-item quantities, electronics, furniture, domestic consumer shipments |
| **IMD Weather & Festival Logistics** | Enriched | Monsoon rainfall probability (15-35% delays), Diwali/Holi festive rush surges |

---

### 6. Train Machine Learning & Deep Learning Models

```bash
# Option A: Master automated pipeline (clean, merge & train all 19 models)
python train.py

# Option B: Train on existing CSV without re-merging
python train.py --skip-clean

# Option C: Interactive model selection console
python train.py --interactive
```

### 🏆 19-Model Benchmark Leaderboard (Evaluated on 36,806 Indian Shipments)

| Rank | Model Name | Category | $R^2$ Score | RMSE (h) | MAE (h) | MAPE (%) | $\pm 30\text{m}$ Tol | Training Time |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 1 | **Voting Regressor** | Ensemble / Meta | **0.9624** | **2.873h** | **1.290h** | 16.1% | 56.5% | 9.8s |
| 🥈 2 | **Random Forest** | Tree-Based | **0.9623** | **2.877h** | **1.281h** | 15.4% | 56.8% | 5.6s |
| 🥉 3 | **Stacking Regressor** | Ensemble / Meta | **0.9622** | **2.879h** | **1.300h** | 16.5% | 56.2% | 95.2s |
| 4 | **Extra Trees Regressor** | Tree-Based | 0.9622 | 2.880h | 1.285h | 15.1% | 56.7% | 3.7s |
| 5 | **CatBoost Regressor** | Boosting | 0.9619 | 2.891h | 1.309h | 17.3% | 55.7% | 5.7s |
| 6 | **LightGBM Regressor** | Boosting | 0.9619 | 2.892h | 1.304h | 16.5% | 56.3% | 1.0s |
| 7 | **Bagging Regressor** | Ensemble | 0.9615 | 2.906h | 1.291h | 14.3% | 56.7% | 4.5s |
| 8 | **Hist Gradient Boosting** | Boosting | 0.9614 | 2.910h | 1.318h | 17.1% | 55.9% | 0.5s |
| 9 | **Gradient Boosting** | Boosting | 0.9613 | 2.914h | 1.321h | 17.3% | 56.1% | 51.6s |
| 10 | **XGBoost Regressor** | Boosting | 0.9611 | 2.919h | 1.315h | 17.4% | 56.0% | 1.2s |
| 11 | **Multi-Layer Perceptron (MLP)** | Deep Learning | 0.9607 | 2.934h | 1.333h | 19.6% | 55.3% | 49.0s |
| 12 | **TabNet Regressor** | Deep Learning | 0.9591 | 2.997h | 1.520h | 45.1% | 47.9% | 75.2s |
| 13 | **Decision Tree** | Tree-Based | 0.9564 | 3.093h | 1.360h | 15.0% | 57.1% | 0.4s |
| 14 | **Support Vector Regressor (SVR)** | Distance-Based | 0.9553 | 3.130h | 1.276h | 16.9% | 66.0% | 19.7s |
| 15 | **K-Nearest Neighbors (KNN)** | Distance-Based | 0.9549 | 3.144h | 1.374h | 15.7% | 59.7% | 1.7s |
| 16 | **Elastic Net** | Baseline | 0.8495 | 5.745h | 3.381h | 118.7% | 20.6% | 0.1s |
| 17 | **Ridge Regression** | Baseline | 0.8495 | 5.745h | 3.383h | 119.1% | 20.3% | 0.0s |
| 18 | **Linear Regression** | Baseline | 0.8495 | 5.745h | 3.383h | 119.1% | 20.3% | 0.0s |
| 19 | **Lasso Regression** | Baseline | 0.8495 | 5.745h | 3.379h | 118.5% | 20.6% | 0.1s |

Outputs saved in `backend/models/saved/`: 19 individual `.pkl` model files, `scaler.pkl`, and `metrics.json`.

---

### 🗺️ Empirical 50km Distance Interval Benchmark (1,000 Predictions / Bracket)

To evaluate which models excel across specific Indian logistics corridors, we execute a distance-stratified benchmark across **48 brackets of 50 km** (0 km to 2,400 km) with **1,000 predictions evaluated per bracket** (**48,000 total test shipments per model**; **912,000 total inferences**).

Run the benchmark anytime with:
```bash
python test_distance_ranges.py --step 50 --samples 1000
```

#### 📍 Operational Distance Tier Routing Rulebook

| Operational Tier | Distance Span | Recommended Model | Best MAE | Accuracy (%) | RMSE (h) | Tol &plusmn;30m | Runner-Up Model | Logistics Domain Context |
|---|:---:|:---|:---:|:---:|:---:|:---:|:---|:---|
| **Hyperlocal & Intra-City Urban** | 0 &ndash; 50 km | **`knn`** | **0.022h** | **97.1%** | 0.110h | 99.1% | `bagging` (0.118h) | Urban Two-Wheeler / Hyperlocal Parcels |
| **Metro Suburbs & Peri-Urban Hubs** | 50 &ndash; 150 km | **`knn`** | **0.165h** | **96.5%** | 0.760h | 91.3% | `decision_tree` (0.566h) | Intra-City Delivery Vans & Couriers |
| **Regional Intercity Corridors** | 150 &ndash; 400 km | **`knn`** | **0.300h** | **97.6%** | 1.070h | 85.6% | `decision_tree` (1.194h) | State Highway Feeder Logistics |
| **Medium-Haul Interstate Freight** | 400 &ndash; 800 km | **`knn`** | **0.564h** | **97.7%** | 1.842h | 82.8% | `decision_tree` (2.269h) | Heavy Multi-Axle Highway Trucks |
| **Long-Haul National Express** | 800 &ndash; 1500 km | **`knn`** | **0.798h** | **97.8%** | 2.621h | 82.9% | `decision_tree` (3.375h) | Dedicated Freight Corridors / Express Cargo |
| **Trans-National Cross-Country** | 1500 &ndash; 2400 km | **`knn`** | **1.295h** | **97.8%** | 3.926h | 80.9% | `decision_tree` (4.548h) | Multi-Modal Intermodal Rail & Air |

#### 🏆 Top 10 Models Across All 48,000 Predictions

| Rank | Model Name | Category | Global MAE | Accuracy (%) | RMSE (h) | Tol &plusmn;30m (%) | Total Wins | Win Rate (%) |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 1 | **`knn`** | Distance-Based | **0.851h** | **97.7%** | 2.914h | 83.1% | 39,178 | 81.6% |
| 🥈 2 | **`decision_tree`** | Decision Tree | **3.218h** | **91.1%** | 5.280h | 19.4% | 1,059 | 2.2% |
| 🥉 3 | **`bagging`** | Tree Ensemble | **3.369h** | **90.6%** | 5.128h | 13.7% | 326 | 0.7% |
| 4 | **`gradient_boosting`** | Gradient Boosted | 3.562h | 89.6% | 5.321h | 12.1% | 261 | 0.5% |
| 5 | **`xgboost`** | Gradient Boosted | 3.628h | 89.8% | 5.588h | 12.6% | 448 | 0.9% |
| 6 | **`voting`** | Meta-Ensemble | 3.817h | 89.4% | 5.906h | 11.5% | 148 | 0.3% |
| 7 | **`extra_trees`** | Tree Ensemble | 3.898h | 89.4% | 6.275h | 13.1% | 1,029 | 2.1% |
| 8 | **`random_forest`** | Tree Ensemble | 3.915h | 89.2% | 6.292h | 12.8% | 936 | 1.9% |
| 9 | **`lightgbm`** | Gradient Boosted | 3.927h | 89.3% | 6.077h | 12.0% | 258 | 0.5% |
| 10 | **`stacking`** | Meta-Ensemble | 3.940h | 89.0% | 6.032h | 11.5% | 194 | 0.4% |

> 📖 **Full Benchmark Documentation:** Detailed tier breakdown and all 48 bracket statistics are available in [`distance_model_benchmark.md`](distance_model_benchmark.md) / [`MODEL_BENCHMARK_50KM.md`](MODEL_BENCHMARK_50KM.md), with raw numerical data in [`range_performance_50km.csv`](range_performance_50km.csv).

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
| `distance_km` | Route distance from OSRM |
| `traffic_duration_min` | Traffic-aware travel time (OSRM Engine Simulation) |
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

### `POST /api/predict/what-if`
Instant sub-second simulation endpoint to evaluate hypothetical traffic, priority, or shipping mode variations.

### `GET /api/history?page=1&per_page=20&traffic=HIGH`
### `POST /api/history`
### `GET /api/analytics/summary` (Includes tolerance accuracy & MAPE)
### `GET /api/analytics/model-comparison` (Includes tolerance accuracy windows & MAPE)
### `GET /api/analytics/traffic-impact`
### `GET /api/analytics/weather-impact`
### `GET /api/health`

---

## 🌟 Advanced Features Implemented

1. **Explainable AI (Tree SHAP Attribution)**: Exact mathematical attribution of delivery duration across distance, traffic congestion, transport mode, priority, and parcel specs.
2. **Tolerance Accuracy Metrics**: Logistics industry-standard operational windows (Within $\pm 15\text{m}$, $\pm 30\text{m}$, $\pm 60\text{m}$) & Mean Absolute Percentage Error (MAPE $\approx 10\%$).
3. **Live "What-If" Scenario Simulator**: Interactive UI controls to simulate how switching from Road to Air or standard to overnight priority impacts ETA without re-geocoding.
4. **Green Logistics Carbon Footprint**: GLEC/DEFRA freight emissions calculator with $CO_2$ kg estimate, eco grade, and tree offset recommendation.
5. **Interactive Transit Route Simulation**: Animated delivery vehicle traversing OpenStreetMap route polyline with live progress tracking.
6. **Logistics Dispatch Waybill**: Printable shipment manifest with tracking identifier, barcode, and verified delivery window.

---

## 🔧 Alternative: Skip Kaggle (Synthetic Data)

If you don't have a Kaggle account, use the synthetic seeder:

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download all 8 Indian logistics & traffic datasets
python download.py

# 3. Clean, merge 184k+ records & train all 19 ML & Deep Learning models
python train.py

# 4. Launch the Web Command Center & Live Dashboard
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
