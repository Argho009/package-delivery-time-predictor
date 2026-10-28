# DeliverAI : Intelligent Logistics & Delivery Duration Predictor

> **DeliverAI** | Python 3.10+ · PyTorch 2.5.1 + CUDA 12.1 · Fine-Tuned ModernBERT-421M SLM (`convaiinnovations/laya-typed-decisions`) · Dual-Tier Meta-Router · 19 Tabular ML/DL Regressors (Voting, Stacking, Random Forest, CatBoost, LightGBM, HistGradientBoosting, Bagging, TabNet, etc.) · OSRM Route Geometry · OpenWeather Telemetry · Flask REST Microservices

DeliverAI is a full-stack, enterprise-grade logistics operating engine designed for the non-linear realities of Indian transport networks. Trained on **184,000+ real-world courier telemetry records** (Delhivery, Amazon India, Bangalore traffic, Indian Railways freight), DeliverAI couples **19 specialized ML/DL regression architectures** with an **On-Device Fine-Tuned Small Language Model (SLM)** that evaluates weather friction, road class, and cargo physics to dispatch each delivery to the optimal algorithmic specialist in **~45 milliseconds**.

---

## 🎓 Academic Deliverables & Project Documentation

* **📄 [50-Page Formal Project Thesis (PDF)](extra/theses/thesis_report_50_pages.pdf)** — Unified 50-page dissertation prepared for **Shri Shankaracharya Institute of Professional Management & Technology (SSIPMT), Raipur** (CSVTU) covering system design, complete 19-model benchmark tournaments, distance discretization, ModernBERT SLM fine-tuning, and carbon auditing.
* **📊 [3rd Project Review Presentation (PPTX)](DeliverAI_Project_Review_3_SSIPMT.pptx)** — Official PowerPoint evaluation slide deck presented for the 5th semester minor project review.
* **📝 [Thesis Source Code (Typst)](extra/theses/thesis_report_50_pages.typ)** — Complete reproducible Typst source for the 50-page thesis.

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

> 📖 **Full Benchmark Documentation:** All 48 bracket statistics, empirical 25km/50km tier tables, Tree SHAP attributions, and green logistics telemetry are fully documented in Chapter 4 & 5 of the **[50-Page Project Thesis Report](extra/theses/thesis_report_50_pages.pdf)**.

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

1. **On-Device Fine-Tuned SLM Meta-Router (ModernBERT-421M)**: Fine-tuned `convaiinnovations/laya-typed-decisions` on 1,540 balanced decision contracts derived from 184k+ real Indian deliveries. Jumped from **19.48% (zero-shot) &rarr; 99.35% accuracy** (+79.87% gain, loss 0.0176, ECE 0.0077), running locally in **~45ms on NVIDIA RTX 3050 CUDA GPU**.
2. **Dual-Tier Dynamic Meta-Router & 4-Tier Self-Healing Hierarchy**:
   - **Tier 1:** Fine-Tuned Laya SLM (CUDA GPU, ~45ms)
   - **Tier 1.5:** Empirical Meta-Classifier (`meta_router.pkl`, CPU, <0.4ms, 100% fidelity)
   - **Tier 2:** Local LM Studio endpoint (`http://127.0.0.1:1234/v1`)
   - **Tier 3:** Deterministic Physical Corridor Heuristic Matrix (0ms, 100% fail-safe)
3. **Live Multi-Model Comparison Studio**: Executes all 12 models simultaneously on any given route, charting algorithm divergence between ensembles, gradient boosters, and linear baselines.
4. **Explainable AI (Tree SHAP Attribution)**: Exact mathematical attribution of delivery duration across distance, traffic congestion, transport mode, priority, and parcel specs.
5. **Tolerance Accuracy Metrics**: Logistics industry-standard operational windows (Within $\pm 15\text{m}$, $\pm 30\text{m}$, $\pm 60\text{m}$) & Mean Absolute Percentage Error (MAPE $\approx 10\%$).
6. **Live "What-If" Scenario Simulator**: Interactive UI controls to simulate how switching from Road to Air or standard to overnight priority impacts ETA without re-geocoding.
7. **Green Logistics Carbon Footprint**: GLEC/DEFRA freight emissions calculator with $CO_2$ kg estimate, eco grade, and tree offset recommendation.
8. **Interactive Transit Route Simulation**: Animated delivery vehicle traversing OpenStreetMap route polyline with live progress tracking.
9. **Logistics Dispatch Waybill**: Printable shipment manifest with tracking identifier, barcode, and verified delivery window.

---

## 🔧 Alternative: Skip Kaggle (Synthetic Data)

If you don't have a Kaggle account, use the synthetic seeder:

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Web Command Center & Live Dashboard
python main.py
```

---

## 📁 Project Structure

```
DeliverAI/
├── main.py                             # Server launcher (FastAPI / Flask gateway)
├── requirements.txt                    # Project dependencies
├── schema.sql                          # Database schema
├── .env.example                        # Environment variable configuration template
├── README.md                           # Main project documentation
├── DeliverAI_Project_Review_3_SSIPMT.pptx # 3rd Review presentation slide deck
│
├── extra/
│   └── theses/
│       ├── thesis_report_50_pages.pdf  # Unified 50-page academic dissertation PDF
│       ├── thesis_report_50_pages.typ  # Typst thesis source code
│       └── README.md                   # Thesis documentation
│
├── backend/
│   ├── app.py                          # Application entry & route registration
│   ├── config.py                       # Configuration loader
│   ├── delivery.db                     # SQLite database
│   ├── data/
│   │   ├── raw/                        # Raw logistics datasets
│   │   ├── processed/                  # Normalized datasets
│   │   ├── download_datasets.py        # Kaggle downloader
│   │   └── process_datasets.py         # Merging & preprocessing
│   ├── models/
│   │   ├── saved/                      # 19 champion trained models (.pkl) & metrics.json
│   │   ├── train.py                    # Multi-model training pipeline
│   │   └── predict.py                  # Singleton inference manager
│   ├── routes/                         # REST API endpoints (predict, history, analytics)
│   ├── services/                       # Geospatial (OSRM) & Weather APIs
│   ├── database/                       # SQLAlchemy models & SQLite setup
│   └── utils/                          # Feature engineering & encoders
│
└── frontend/
    ├── index.html                      # Main portal
    ├── predict.html                    # Delivery time predictor
    ├── dashboard.html                  # Live fleet telemetry dashboard
    ├── copilot.html                    # AI dispatch copilot interface
    ├── history.html                    # Prediction history & logs
    ├── css/                            # Custom vanilla stylesheets
    └── js/                             # Client-side routing, charts & map rendering
```
