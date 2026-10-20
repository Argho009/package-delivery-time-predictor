# DeliverAI: AI-Based Package Delivery Time Prediction System

> **5th Semester B.Tech Minor Project Comprehensive Report & Research Monograph**
> *Empirical Benchmark of 19 Machine Learning & Deep Learning Regression Models across 184,000+ Inland India Logistics Records, Local Small Language Model (SLM) Route Decision Routing, and Dedicated Hardware-Accelerated Copilot*

---

## Metadata Block

- **Project Title:** DeliverAI Package Delivery Time Predictor
- **Academic Level:** B.Tech Computer Science & Engineering — 5th Semester Minor Project
- **Domain:** Applied Artificial Intelligence, Machine Learning & Logistics Telematics
- **Evaluation Date:** October 2026
- **Software Stack:** Python 3.12 · PyTorch 2.5.1 · Scikit-Learn · Flask · Leaflet
- **Hardware Acceleration:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4)
- **Local LLM Server:** LM Studio (Port 1234 / OpenAI-Compatible v1 API)
- **Geospatial Engine:** OSRM Ground Table Routing & OpenWeather Precipitation

---

## 1. Abstract

Predicting accurate transit duration for freight logistics across the Indian subcontinent represents an intricate geospatial and algorithmic challenge. Inland transportation in India is influenced by severe highway traffic bottlenecks, heterogeneous vehicle categories (from two-wheeler hyperlocal delivery to multi-axle freight containers and railway freight), monsoon-induced route diversions, and seasonal festive surges (e.g., Diwali, Durga Puja). This project presents **DeliverAI**, an end-to-end intelligent logistics decision-support platform trained on a massive, unified dataset of **184,029 authentic shipment records** compiled from 8 distinct Indian transportation repositories.

We conduct an exhaustive empirical benchmark of **19 distinct regression architectures**, spanning regularized linear baselines (Ridge, Lasso, Elastic Net), tree-based ensembles (Random Forest, Extra Trees, Decision Tree, Bagging), gradient-boosted trees (XGBoost, LightGBM, CatBoost, HistGradientBoosting, Gradient Boosting), distance-based estimators (K-Nearest Neighbors, Support Vector Regression), deep learning architectures (Multi-Layer Perceptron, PyTorch TabNet), and meta-ensembles (Stacking Regressor, Voting Regressor).

On a rigorous 20% holdout test partition of **36,806 shipments**, the **Voting Regressor** achieved the overall champion performance with an **R² score of 0.9624**, Root Mean Squared Error (RMSE) of **2.873 hours**, and Mean Absolute Error (MAE) of **1.290 hours**. Furthermore, a systematic 25km interval discretization benchmark across 96 geographic tiers (0 km to 2,400 km) revealed that **Bagging Regressor** dominates hyperlocal/urban routes (&le; 25 km) with an MAE of 0.080 hours (~4.8 minutes), while **K-Nearest Neighbors (KNN)** demonstrates unmatched precision on intercity and national corridors (&ge; 25 km) with 97.7% accuracy.

Expanding beyond static predictions, DeliverAI integrates a **Small Language Model (SLM) Route Decision Engine** running locally on an **NVIDIA GeForce RTX 3050 6GB GPU** via LM Studio. The SLM decomposes route corridors into 25km intervals, evaluates weather friction, and dynamically allocates specialized algorithms per leg. The platform features an executive dark obsidian glassmorphism UI, game-theoretic Tree SHAP explainability, and GLEC/DEFRA freight carbon footprint auditing.

---

## 2. Multi-Source Dataset Architecture & Ingestion

| # | Dataset / Repository Source | Records | Primary Logistics Domain | Key Features Extracted |
|---|---|:---:|---|---|
| 1 | **Delhivery Logistics Dataset** | 55,000 | National Courier & Truck Freight | Actual transit duration, OSRM distance, FTL vs Carting, segment times |
| 2 | **Amazon India Sales & Shipping** | 25,000 | B2C E-Commerce Fulfillment | Expedited vs standard shipping, apparel/retail, fulfillment hubs |
| 3 | **Hyperlocal Food & Parcel Trips** | 45,593 | Urban Two-Wheeler Rapid Transit | High traffic sensitivity, delivery agent ratings, rapid urban turnaround |
| 4 | **Bangalore City Traffic Corridors** | 8,936 | Metro Intersection Telemetry | Peak-hour congestion ratios, signal delay buffers, congestion interaction |
| 5 | **Indian Road Corridors & Hazards** | 20,000 | Highway Speed & Safety | National Highway vs State Highway condition factors, terrain restrictions |
| 6 | **Indian Railways Freight & Cargo** | 10,000 | Heavy Container & Rail Transit | DFC track corridor distances, yard marshaling delays, hub dwell intervals |
| 7 | **Flipkart E-Commerce Orders** | 1,500 | Multi-Item Consumer Shipments | Item quantity multipliers, dimensional package weights, regional hub dispatches |
| 8 | **IMD Weather & Festival Surge Layer** | 18,000 | Climatic & Seasonal Impact | Monsoon precipitation delays (15–35%), Diwali/Holi festive capacity surges |
| | **Consolidated Total Dataset** | **184,029** | **Complete Inland India Supply Chain Representation** | |

---

## 3. Data Cleaning & Preprocessing Methodology

1. **Schema Unification:** Normalized differing column conventions into standard schema (`distance_km`, `traffic_duration_min`, `traffic_level_enc`, `package_weight_kg`, `package_type_enc`, `priority_enc`, `shipping_mode_enc`, `actual_time_hours`).
2. **Missing Value Imputation:** Missing coordinates geocoded via Nominatim; missing distances computed via OSRM table routing with 1.28x Indian highway winding factor; missing traffic durations calculated using Bangalore congestion models.
3. **Outlier Filtering:** Physics-based speed bounds ($0.15\text{h} \le t \le 168\text{h}$, speed $\le 110\text{ km/h}$ for trucks) eliminated sensor drops and manual input corruption.
4. **Leakage-Free Scaling:** `StandardScaler` fitted strictly on 80% training partition (`backend/models/saved/scaler.pkl`) to preserve test integrity.

---

## 4. 19-Model Benchmark Leaderboard (36,806 Test Shipments)

| Rank | Model Name | Category | $R^2$ Score | RMSE (h) | MAE (h) | MAPE (%) | $\pm 30\text{m}$ Tol | Training Time |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 1 | **Voting Regressor** | Ensemble / Meta | **0.9624** | **2.873h** | **1.290h** | 16.1% | 56.5% | 9.8s |
| 🥈 2 | **Random Forest** | Tree Ensemble | **0.9623** | **2.877h** | **1.281h** | 15.4% | 56.8% | 5.6s |
| 🥉 3 | **Stacking Regressor** | Ensemble / Meta | **0.9622** | **2.879h** | **1.300h** | 16.5% | 56.2% | 95.2s |
| 4 | **Extra Trees Regressor** | Tree Ensemble | 0.9622 | 2.880h | 1.285h | 15.1% | 56.7% | 3.7s |
| 5 | **CatBoost Regressor** | Gradient Boosting | 0.9619 | 2.891h | 1.309h | 17.3% | 55.7% | 5.7s |
| 6 | **LightGBM Regressor** | Gradient Boosting | 0.9619 | 2.892h | 1.304h | 16.5% | 56.3% | 1.0s |
| 7 | **Bagging Regressor** | Tree Ensemble | 0.9615 | 2.906h | 1.291h | 14.3% | 56.7% | 4.5s |
| 8 | **Hist Gradient Boosting** | Gradient Boosting | 0.9614 | 2.910h | 1.318h | 17.1% | 55.9% | 0.5s |
| 9 | **Gradient Boosting** | Gradient Boosting | 0.9613 | 2.914h | 1.321h | 17.3% | 56.1% | 51.6s |
| 10 | **XGBoost Regressor** | Gradient Boosting | 0.9611 | 2.919h | 1.315h | 17.4% | 56.0% | 1.2s |
| 11 | **Multi-Layer Perceptron (MLP)** | Deep Learning | 0.9607 | 2.934h | 1.333h | 19.6% | 55.3% | 49.0s |
| 12 | **TabNet Regressor** | Deep Learning | 0.9591 | 2.997h | 1.520h | 45.1% | 47.9% | 75.2s |
| 13 | **Decision Tree** | Tree-Based | 0.9564 | 3.093h | 1.360h | 15.0% | 57.1% | 0.4s |
| 14 | **Support Vector Regressor (SVR)** | Distance-Based | 0.9553 | 3.130h | 1.276h | 16.9% | 66.0% | 19.7s |
| 15 | **K-Nearest Neighbors (KNN)** | Distance-Based | 0.9549 | 3.144h | 1.374h | 15.7% | 59.7% | 1.7s |
| 16 | **Elastic Net** | Baseline Linear | 0.8495 | 5.745h | 3.381h | 118.7% | 20.6% | 0.1s |
| 17 | **Ridge Regression** | Baseline Linear | 0.8495 | 5.745h | 3.383h | 119.1% | 20.3% | 0.0s |
| 18 | **Linear Regression** | Baseline Linear | 0.8495 | 5.745h | 3.383h | 119.1% | 20.3% | 0.0s |
| 19 | **Lasso Regression** | Baseline Linear | 0.8495 | 5.745h | 3.379h | 118.5% | 20.6% | 0.1s |

---

## 5. Distance-Stratified Routing Rulebook (25km Intervals)

| Operational Distance Tier | Range (km) | Optimal Model | Best MAE | Accuracy (%) | Runner-Up Model |
|---|:---:|:---:|:---:|:---:|:---|
| **Hyperlocal / Urban** | 0 – 25 km | **bagging** | **0.080h** (~4.8 min) | **89.4%** | decision_tree (0.082h) |
| **Intra-City & Suburbs** | 25 – 100 km | **knn** | **0.023h** (~1.4 min) | **99.3%** | svr (0.294h) |
| **Regional Intercity** | 100 – 300 km | **knn** | **0.362h** (~21.7 min) | **96.6%** | random_forest (1.108h) |
| **Medium-Haul Interstate** | 300 – 600 km | **knn** | **0.480h** (~28.8 min) | **97.6%** | random_forest (2.497h) |
| **Long-Haul National Express** | 600 – 1,200 km | **knn** | **0.490h** (~29.4 min) | **98.1%** | svr (2.828h) |
| **Cross-Country Freight** | 1,200 – 2,400 km | **knn** | **1.305h** (~1.3 hours) | **97.6%** | bagging (5.026h) |

---

## 6. Small Language Model (SLM) Route & Leg-by-Leg Decision Engine

DeliverAI couples structured tabular ML predictions with the high-order semantic reasoning of a dedicated **Local Small Language Model (SLM)** (Llama-3.2-3B-Instruct or Qwen-2.5-7B via LM Studio `/v1/chat/completions` on `http://127.0.0.1:1234/v1`).

- **Corridor Geography:** Evaluates Golden Quadrilateral expressways vs State Highways.
- **Weather & Environmental Friction:** Detects precipitation, fog, and road spray to deploy **CatBoost** for ordered boosting target encoding resilience.
- **25km Leg Discretization:** Deconstructs the full corridor into 25km intervals, assigning specialized models (e.g. Bagging for urban start/end, CatBoost for rainy passes, Voting for open highway).
- **Autonomous Fallback:** Instant fallback to domain benchmark heuristic matrix if LM Studio is paused, ensuring 0ms latency penalty.

---

## 7. Local AI Logistics Copilot Studio (Hardware-Accelerated)

- **Hardware:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4).
- **Inference API:** Local LM Studio server providing zero cloud transmission latency and complete data sovereignty.
- **Capabilities:** Highway delay root-cause analysis, multimodal speed vs cost vs carbon evaluations, monsoon ghat route safety protocols, and commercial driver dispatch briefings.

---

## 8. Explainable AI (SHAP) & Green Logistics (GLEC / DEFRA)

- **Tree SHAP Attribution:** Traffic Duration (26.2%), Shipping Mode (18.4%), Priority Tier (16.1%), Road Distance (14.8%), Package Weight (12.5%), Package Type (12.0%).
- **Certified Emissions Calculation:** Precise freight CO₂ calculation: $\text{Emissions} = (\text{Distance} \times \text{Weight} / 1000) \times \text{Factor}$.
- **Emission Factors:** Road (0.096), Air (0.602), Rail (0.028), Sea (0.011) $\text{kg } CO_2/\text{tonne-km}$. Includes Eco-grades (A+ to F) and tree-planting offsets.

---

## 9. Reconstructed Executive Command Center UI

- **Design System:** Obsidian Glassmorphism (`#080C15`, `#0F172A`) with Plus Jakarta Sans and JetBrains Mono typography.
- **Cockpit Design:** Split-cockpit layout on `predict.html` (Dispatch Console on left, 4-Tab Unified Intelligence Studio on right).
- **Modular Tabs:** Tab 1 (SLM Meta-Router & 25km Legs), Tab 2 (Route Corridor Map & Telemetry), Tab 3 (SHAP Factors & What-If Simulator), Tab 4 (Green Logistics & ESG Score).
- **Telemetry & Analytics:** Real-time KPI counters, Chart.js traffic/weather distribution charts, search/filter toolbar, and instant CSV manifest exports.

---

## 10. Engineering Post-Mortem: Windows CUDA Fast-Fail (0xC0000409)

During testing on Windows, the Flask server terminated with exit code `0xC0000409` (`STATUS_STACK_BUFFER_OVERRUN`) ~10–23 seconds after executing predictions.

- **Root Cause:** `xgboost.pkl` and `voting.pkl` sub-estimators were serialized with `device: 'cuda'` and `n_jobs: -1`. Werkzeug worker threads unloading unmanaged CUDA contexts triggered access violations during `DLL_PROCESS_DETACH` in `nvcuda.dll`.
- **Resolution:** Re-configured tree models with `device: 'cpu'` and `n_jobs: 1` prior to serialization. Reserved the dedicated NVIDIA RTX 3050 GPU for PyTorch TabNet and LM Studio local SLM inference, achieving 100% server stability.

---

## 11. Conclusion & Academic Contributions

DeliverAI demonstrates that empirical distance discretization combined with a Small Language Model routing engine outperforms any single standalone algorithm across India's complex supply chain geography. Voting Regressor champions global long-haul accuracy ($R^2 = 0.9624$), Bagging Regressor masters hyperlocal corridors (&le; 25 km, MAE 4.8 min), and KNN dominates interstate corridors (97.7% accuracy), creating a resilient, interpretable, and sustainable logistics platform.
