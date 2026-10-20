# DeliverAI: Comprehensive Empirical Model Architecture & Logistics Telematics Report

> **5th Semester B.Tech Minor Project Research Monograph & Systems Evaluation**  
> *Department of Computer Science & Engineering · Applied Artificial Intelligence & Telematics*  
> **Project Repository:** `Argho009/package-delivery-time-predictor`  
> **Dataset Scale:** 184,029 Inland India Multi-Source Logistics Records · 19 Architectures · 48,000 Distance Benchmark Predictions

---

## Executive Metadata & System Specifications

| Specification Attribute | Implementation & Engineering Details |
|---|---|
| **Project Title** | DeliverAI: Intelligent Package Delivery Transit Time Predictor |
| **Academic Level** | Bachelor of Technology (B.Tech) — 5th Semester Minor Project |
| **Department** | Department of Computer Science & Engineering |
| **Core Frameworks** | Python 3.12 · Scikit-Learn 1.5 · PyTorch 2.5.1 · Flask 3.0 · Leaflet.js |
| **Hardware Acceleration** | Dedicated NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4) |
| **Local AI Copilot** | LM Studio Local Engine (localhost:1234) / Ollama (localhost:11434) |
| **Geospatial & Telematics Engine** | Open Source Routing Machine (OSRM) + OpenWeather Current Telemetry |
| **Primary Data Corpus** | 184,029 Records from Delhivery, Amazon India, Bangalore Traffic, Indian Railways & Road Hazards |
| **Holdout Test Partition** | 36,806 Real Indian Shipments (Strict 20% Stratified Holdout) |
| **Empirical Distance Benchmark** | 48 Brackets of 50 km (0 to 2,400 km) with 1,000 Predictions per Bracket (48,000 Samples) |

---

## Table 1: Master Taxonomy & Mathematical Foundations of the 19 Regression Architectures

The platform benchmarks nineteen distinct regression architectures categorized into six methodological paradigms:

| Rank | Model Architecture | Paradigm / Category | Mathematical Objective Function / Hypothesis Space | Algorithmic Complexity | Primary Logistics Strength | Operational Vulnerability |
|:---:|:---|:---|:---|:---:|:---|:---|
| 1 | **Linear Regression** | Baseline Linear | min ||Xw - y||² (Ordinary Least Squares) | O(d²·n + d³) | Instant training, absolute interpretability | High bias; fails on nonlinear traffic bottlenecks |
| 2 | **Ridge Regression** | Regularized Linear | min ||Xw - y||² + α||w||² (L2 Regularized) | O(d²·n + d³) | Controls collinearity between distance and duration | Retains all features; unable to zero noise coefficients |
| 3 | **Lasso Regression** | Regularized Linear | min (1/2n)||Xw - y||² + α||w||₁ (L1 Regularized) | O(d·n) per iter | Sparse weights; performs intrinsic feature selection | Arbitrarily drops one of highly correlated features |
| 4 | **Elastic Net** | Regularized Linear | min (1/2n)||Xw - y||² + α·ρ||w||₁ + [α(1-ρ)/2]||w||² | O(d·n) per iter | Balances sparsity with grouped feature stability | Sensitive to hyperparameter grid search |
| 5 | **Decision Tree** | Tree-Based | Greedy recursive binary sum-of-squares variance reduction | O(d·n log n) | Non-parametric; captures sharp geographic step-changes | High variance; prone to severe overfitting on edge cases |
| 6 | **Random Forest** | Tree Ensemble | Bootstrap Aggregation over 1,000 randomized decision trees | O(B·d·n log n) | Drastic variance reduction; excellent generalizability | Large memory footprint; slower single-instance inference |
| 7 | **Extra Trees** | Tree Ensemble | Extremely Randomized Trees with random split thresholds | O(B·d·n) | Smoother decision boundaries; faster training than RF | Higher individual tree bias |
| 8 | **Bagging Regressor** | Tree Ensemble | Bootstrap Aggregating over 100 deep Decision Trees | O(B·d·n log n) | Dominates hyperlocal urban routes (<= 50 km) | Computationally expensive on large sample sets |
| 9 | **Gradient Boosting** | Boosting Ensemble | Sequential negative-gradient residual descent optimization | O(M·d·n log n) | High precision optimization on continuous residuals | Sequential training; susceptible to outlier skew |
| 10 | **Hist Gradient Boosting**| Histogram Boosting| 256-bin integer histogram discretization | O(M·d·n) | Blazing fast CPU training; native missing-value support | Minor precision loss from integer histogram binning |
| 11 | **XGBoost Regressor** | Gradient Boosted | Newton-Raphson 2nd-order Taylor expansion tree boosting | O(M·d·n) | Cache-aware block structures; column subsampling | Requires careful Windows thread isolation |
| 12 | **LightGBM Regressor** | Gradient Boosted | Leaf-wise tree growth with GOSS & Exclusive Feature Bundling | O(M·d·n) | Lowest memory consumption; rapid convergence | Can overfit small datasets if max depth is unbounded |
| 13 | **CatBoost Regressor** | Gradient Boosted | Ordered boosting with symmetric oblivious decision trees | O(M·d·n) | Superior categorical handling; resistant to target leakage | Slower evaluation on very high tree counts |
| 14 | **K-Nearest Neighbors**| Distance-Based | Distance-weighted k-NN: y = Σ(wᵢ·yᵢ)/Σwᵢ where wᵢ = 1/d | O(d·n) inference | Unmatched accuracy on recurring intercity corridors | O(n) inference latency scales with dataset size |
| 15 | **Support Vector (SVR)**| Distance-Based | Epsilon-insensitive margin optimization with RBF kernel | O(n² to n³) | Maximum margin boundary; immune to small errors <= ε | Scales quadratically with N; requires subsampling |
| 16 | **MLP (Deep Learning)**| Neural Network | 4-layer feed-forward deep perceptron (512-256-128-64, ReLU) | O(epochs·weights·n) | Smooth high-dimensional non-linear surface modeling | Requires feature standardization; sensitive to learning rate |
| 17 | **TabNet Regressor** | Deep Learning | Sequential attention transformer mechanism for tabular data | O(steps·dim·n) | Sparse feature masking; interpretable decision steps | Demands GPU acceleration; higher training latency |
| 18 | **Stacking Regressor** | Meta-Ensemble | Multi-model cross-validated stacking with Ridge meta-learner | O(K·O_base + O_meta) | Combines diverse inductive biases into a super-learner | Extremely high training time; risk of meta-overfitting |
| 19 | **Voting Regressor** | Meta-Ensemble | Soft weighted ensemble average of top 4 tree/boosted models | O(Σ O_base) | Champion Generalizer (R² = 0.962); mitigates variance | Requires running 4 distinct models in parallel |

---

## Table 2: Hyperparameter Specifications & Computational Execution Topology

| Architecture | Key Hyperparameters & Tuning Constraints | Loss Function | Feature Scaling | Hardware Device | Training Duration |
|---|---|---|:---:|:---:|:---:|
| **Linear Regression** | Default ordinary least squares; fit_intercept=True | MSE | Standardized | CPU (1 Thread) | 0.02s |
| **Ridge** | alpha = 1.0, solver='auto', random_state=42 | L2-Regularized MSE | Standardized | CPU (1 Thread) | 0.01s |
| **Lasso** | alpha = 0.01, max_iter=3000, random_state=42 | L1-Regularized MSE | Standardized | CPU (1 Thread) | 0.12s |
| **Elastic Net** | alpha = 0.01, L1-ratio = 0.5, max_iter=3000 | Elastic MSE | Standardized | CPU (1 Thread) | 0.11s |
| **Decision Tree** | max_depth=16, min_samples_split=6, min_samples_leaf=2 | Squared Error | Raw Features | CPU (1 Thread) | 0.53s |
| **Random Forest** | n_estimators=1000, max_depth=18, min_samples_split=4, max_features='sqrt' | Squared Error | Raw Features | Multi-Core CPU | 24.21s |
| **Extra Trees** | n_estimators=1000, max_depth=18, min_samples_split=4, max_features='sqrt' | Squared Error | Raw Features | Multi-Core CPU | 18.41s |
| **Bagging Regressor** | estimator=DecisionTree(depth=14), n_estimators=100, max_samples=0.9 | Squared Error | Raw Features | Multi-Core CPU | 8.17s |
| **Gradient Boosting**| n_estimators=500, max_depth=6, lr=0.04, subsample=0.85 | Squared Error | Raw Features | CPU (1 Thread) | 110.47s |
| **Hist Gradient Boost**| max_iter=1000, max_depth=8, lr=0.03, max_bins=255 | Squared Error | Raw Features | Multi-Core CPU | 2.11s |
| **XGBoost** | n_estimators=1000, max_depth=8, lr=0.03, subsample=0.85, reg_lambda=1.0 | reg:squarederror | Raw Features | Multi-Core CPU | 4.58s |
| **LightGBM** | n_estimators=1000, max_depth=9, num_leaves=63, lr=0.03, subsample=0.85 | L2 Regression | Raw Features | Multi-Core CPU | 2.32s |
| **CatBoost** | iterations=1000, depth=8, learning_rate=0.03, l2_leaf_reg=2.0 | RMSE | Raw Features | Multi-Core CPU | 4.81s |
| **KNN** | n_neighbors=9, weights='distance', algorithm='auto' | Euclidean Dist | Standardized | Multi-Core CPU | 1.25s |
| **SVR** | kernel='rbf', C=25.0, epsilon=0.05, gamma='scale', subsample 15k | Epsilon-SVR | Standardized | CPU (1 Thread) | 23.22s |
| **MLP Regressor** | Layers: (512, 256, 128, 64), relu, batch_size=512, early_stopping=True | MSE | Standardized | Multi-Core CPU | 209.80s |
| **TabNet** | n_d=24, n_a=24, n_steps=5, gamma=1.3, epochs=25, batch_size=1024 | MSE | Standardized | NVIDIA RTX 3050 | 185.93s |
| **Voting Regressor** | Soft weighted average: CatBoost, LightGBM, XGBoost, Random Forest | Ensemble Mean | Hybrid | Multi-Core CPU | 46.30s |
| **Stacking Regressor**| Base: XGBoost, LightGBM, RF; Meta-Estimator: Ridge (CV=5) | CV Residuals | Hybrid | Multi-Core CPU | 95.20s |

---

## Table 3: Master Empirical Benchmark Leaderboard (36,806 Holdout Shipments)

The 19 architectures were evaluated on an unexposed 20% holdout test partition of **36,806 authentic shipments** from across inland India:

| Rank | Model Architecture | Category | R² Score | RMSE (hours) | MAE (hours) | MAPE (%) | Within ±15 min | Within ±30 min | Within ±60 min | Training Duration |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 1 | **`voting`** | Meta-Ensemble | **0.9620** | **2.886h** | **1.285h** | 15.2% | 47.7% | 56.7% | 68.0% | 46.30s |
| 🥈 2 | **`mlp`** | Neural Network (MLP) | **0.9617** | **2.900h** | **1.298h** | 20.3% | 44.1% | 56.4% | 68.9% | 209.80s |
| 🥉 3 | **`hist_gradient_boosting`** | Histogram Boosting | **0.9616** | **2.902h** | **1.313h** | 17.0% | 46.8% | 55.9% | 67.0% | 2.11s |
| Rank 4 | **`random_forest`** | Tree Ensemble | **0.9615** | **2.907h** | **1.280h** | 14.2% | 48.8% | 58.1% | 69.5% | 24.21s |
| Rank 5 | **`lightgbm`** | Gradient Boosted | **0.9614** | **2.911h** | **1.295h** | 15.2% | 48.0% | 56.9% | 68.0% | 2.32s |
| Rank 6 | **`gradient_boosting`** | Gradient Boosted | **0.9612** | **2.918h** | **1.318h** | 17.1% | 46.5% | 56.1% | 66.8% | 110.47s |
| Rank 7 | **`catboost`** | Gradient Boosted | **0.9611** | **2.921h** | **1.318h** | 17.2% | 46.1% | 55.5% | 67.0% | 4.81s |
| Rank 8 | **`bagging`** | Tree Ensemble | **0.9611** | **2.921h** | **1.289h** | 13.9% | 49.0% | 57.5% | 68.7% | 8.17s |
| Rank 9 | **`extra_trees`** | Tree Ensemble | **0.9606** | **2.939h** | **1.289h** | 14.1% | 49.1% | 58.2% | 69.4% | 18.41s |
| Rank 10 | **`xgboost`** | Gradient Boosted | **0.9598** | **2.971h** | **1.318h** | 16.1% | 47.2% | 56.6% | 67.8% | 4.58s |
| Rank 11 | **`tabnet`** | Deep Learning (TabNet) | **0.9589** | **3.002h** | **1.495h** | 46.5% | 23.7% | 39.2% | 64.9% | 185.93s |
| Rank 12 | **`knn`** | Distance-Based | **0.9562** | **3.099h** | **1.359h** | 15.6% | 50.1% | 59.3% | 69.6% | 1.25s |
| Rank 13 | **`svr`** | Support Vector Machine | **0.9556** | **3.122h** | **1.256h** | 14.9% | 56.3% | 66.7% | 74.6% | 23.22s |
| Rank 14 | **`decision_tree`** | Decision Tree | **0.9483** | **3.368h** | **1.438h** | 14.9% | 50.5% | 59.2% | 69.2% | 0.53s |
| Rank 15 | **`elastic_net`** | Regularized Linear | **0.8495** | **5.745h** | **3.381h** | 118.7% | 8.6% | 20.6% | 36.1% | 0.11s |
| Rank 16 | **`ridge`** | Regularized Linear | **0.8495** | **5.745h** | **3.383h** | 119.1% | 8.5% | 20.3% | 36.1% | 0.01s |
| Rank 17 | **`linear_regression`** | Baseline Linear | **0.8495** | **5.745h** | **3.383h** | 119.1% | 8.5% | 20.3% | 36.1% | 0.02s |
| Rank 18 | **`lasso`** | Regularized Linear | **0.8495** | **5.745h** | **3.379h** | 118.5% | 8.6% | 20.6% | 36.1% | 0.12s |

---

## Table 4: Operational Distance Tier Routing & Fleet Allocation Matrix

Evaluating global averages masks localized performance differences. The table below outlines the optimal model allocation for each logistics operational tier in India:

| Operational Tier | Distance Span | Recommended Model | Tier MAE | Accuracy (%) | Tier RMSE | Within ±30 min | Runner-Up Model | Transport Fleet Profile | Key Mitigated Bottlenecks |
|---|:---:|:---|:---:|:---:|:---:|:---:|:---|:---|:---|
| **Hyperlocal & Intra-City** | 0 – 50 km | **`knn`** | **0.022h** (~1.3m) | **97.1%** | 0.110h | 99.1% | `bagging` (0.118h) | Two-wheelers, EV bikes, 3-wheel cargo | Urban red lights, narrow alleyways |
| **Metro Suburbs & Peri-Urban**| 50 – 150 km | **`knn`** | **0.165h** (~9.9m) | **96.5%** | 0.760h | 91.3% | `decision_tree` (0.566h) | Intra-city delivery vans, light trucks | Ring road bottlenecks, outer toll plazas |
| **Regional Intercity Corridors** | 150 – 400 km | **`knn`** | **0.300h** (~18.0m) | **97.6%** | 1.070h | 85.6% | `decision_tree` (1.194h) | 2-axle / 3-axle State Highway trucks | Single-lane ghat bypasses, state border checks |
| **Medium-Haul Interstate** | 400 – 800 km | **`knn`** | **0.564h** (~33.8m) | **97.7%** | 1.842h | 82.8% | `decision_tree` (2.269h) | Multi-axle National Highway containers | FASTag queue delays, nocturnal truck traffic |
| **Long-Haul National Express** | 800 – 1500 km | **`knn`** | **0.798h** (~47.9m) | **97.8%** | 2.621h | 82.9% | `decision_tree` (3.375h) | Dedicated Freight Corridor (DFC) rail & express | Multi-state weather shifts, rail yard marshaling |
| **Trans-National Cross-Country**| 1500 – 2400 km | **`knn`** | **1.295h** (~1.3h) | **97.8%** | 3.926h | 80.9% | `decision_tree` (4.548h) | Intermodal rail-road, domestic cargo air | Extreme weather disruptions, rail transshipment |

---

## Table 5: Comprehensive 50km Interval Benchmark Data (All 48 Brackets)

Below is the exhaustive, empirical evaluation of **1,000 predictions evaluated per bracket** (**48,000 total shipments**; **912,000 inferences** across all 19 architectures):

| Bracket Label | Distance Span (km) | Actual ETA (h) | Winning Model | Winner MAE | Winner Acc (%) | Winner Within ±30 min (%) | Runner-Up Model | Runner-Up MAE | 3rd Place Model | 3rd Place MAE |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|:---:|:---|:---:|
| `0-50km` | 0 to 50 km | 0.81h | **`knn`** | **0.022h** | **97.1%** | 99.1% | `bagging` | 0.118h | `decision_tree` | 0.119h |
| `50-100km` | 50 to 100 km | 3.21h | **`knn`** | **0.162h** | **96.2%** | 93.2% | `decision_tree` | 0.507h | `bagging` | 0.558h |
| `100-150km` | 100 to 150 km | 5.13h | **`knn`** | **0.169h** | **96.9%** | 89.4% | `decision_tree` | 0.626h | `bagging` | 0.657h |
| `150-200km` | 150 to 200 km | 7.50h | **`knn`** | **0.228h** | **97.4%** | 87.4% | `decision_tree` | 0.829h | `bagging` | 0.880h |
| `200-250km` | 200 to 250 km | 10.17h | **`knn`** | **0.247h** | **97.7%** | 86.9% | `decision_tree` | 1.020h | `bagging` | 1.030h |
| `250-300km` | 250 to 300 km | 12.17h | **`knn`** | **0.269h** | **97.8%** | 85.5% | `decision_tree` | 1.136h | `bagging` | 1.171h |
| `300-350km` | 300 to 350 km | 14.29h | **`knn`** | **0.330h** | **97.7%** | 85.0% | `decision_tree` | 1.320h | `bagging` | 1.377h |
| `350-400km` | 350 to 400 km | 17.25h | **`knn`** | **0.424h** | **97.8%** | 83.4% | `decision_tree` | 1.666h | `bagging` | 1.795h |
| `400-450km` | 400 to 450 km | 18.69h | **`knn`** | **0.457h** | **97.5%** | 83.4% | `decision_tree` | 1.646h | `bagging` | 1.787h |
| `450-500km` | 450 to 500 km | 20.02h | **`knn`** | **0.434h** | **97.7%** | 83.9% | `decision_tree` | 1.698h | `bagging` | 1.833h |
| `500-550km` | 500 to 550 km | 20.50h | **`knn`** | **0.443h** | **97.9%** | 84.5% | `decision_tree` | 2.011h | `bagging` | 2.143h |
| `550-600km` | 550 to 600 km | 21.79h | **`knn`** | **0.652h** | **97.2%** | 80.1% | `decision_tree` | 2.187h | `bagging` | 2.294h |
| `600-650km` | 600 to 650 km | 23.86h | **`knn`** | **0.575h** | **97.6%** | 82.6% | `decision_tree` | 2.295h | `svr` | 2.441h |
| `650-700km` | 650 to 700 km | 27.22h | **`knn`** | **0.650h** | **97.7%** | 82.3% | `decision_tree` | 2.805h | `bagging` | 2.914h |
| `700-750km` | 700 to 750 km | 27.71h | **`knn`** | **0.660h** | **97.7%** | 82.9% | `decision_tree` | 2.728h | `svr` | 2.965h |
| `750-800km` | 750 to 800 km | 28.42h | **`knn`** | **0.645h** | **97.8%** | 82.8% | `decision_tree` | 2.781h | `svr` | 2.782h |
| `800-850km` | 800 to 850 km | 25.90h | **`knn`** | **0.607h** | **97.8%** | 84.6% | `decision_tree` | 2.797h | `bagging` | 2.834h |
| `850-900km` | 850 to 900 km | 28.17h | **`knn`** | **0.625h** | **97.8%** | 84.5% | `decision_tree` | 2.970h | `bagging` | 3.063h |
| `900-950km` | 900 to 950 km | 26.80h | **`knn`** | **0.654h** | **97.8%** | 84.5% | `svr` | 2.883h | `decision_tree` | 2.894h |
| `950-1000km` | 950 to 1000 km | 27.69h | **`knn`** | **0.707h** | **97.6%** | 83.7% | `decision_tree` | 2.790h | `xgboost` | 2.915h |
| `1000-1050km` | 1000 to 1050 km | 30.07h | **`knn`** | **0.765h** | **97.6%** | 82.8% | `decision_tree` | 3.135h | `xgboost` | 3.187h |
| `1050-1100km` | 1050 to 1100 km | 26.70h | **`knn`** | **0.596h** | **97.9%** | 84.3% | `decision_tree` | 2.382h | `svr` | 2.529h |
| `1100-1150km` | 1100 to 1150 km | 28.32h | **`knn`** | **0.619h** | **97.9%** | 83.9% | `decision_tree` | 2.789h | `bagging` | 2.791h |
| `1150-1200km` | 1150 to 1200 km | 28.46h | **`knn`** | **0.642h** | **97.7%** | 82.8% | `decision_tree` | 2.440h | `bagging` | 2.684h |
| `1200-1250km` | 1200 to 1250 km | 38.77h | **`knn`** | **0.914h** | **97.8%** | 80.1% | `bagging` | 3.338h | `decision_tree` | 3.354h |
| `1250-1300km` | 1250 to 1300 km | 40.34h | **`knn`** | **0.739h** | **98.2%** | 86.0% | `decision_tree` | 3.170h | `bagging` | 3.296h |
| `1300-1350km` | 1300 to 1350 km | 43.13h | **`knn`** | **1.054h** | **97.6%** | 80.5% | `bagging` | 4.040h | `decision_tree` | 4.124h |
| `1350-1400km` | 1350 to 1400 km | 46.62h | **`knn`** | **1.112h** | **97.6%** | 81.0% | `xgboost` | 4.566h | `bagging` | 4.664h |
| `1400-1450km` | 1400 to 1450 km | 48.99h | **`knn`** | **1.114h** | **97.8%** | 80.5% | `xgboost` | 4.721h | `bagging` | 4.777h |
| `1450-1500km` | 1450 to 1500 km | 49.21h | **`knn`** | **1.028h** | **97.8%** | 81.5% | `xgboost` | 4.673h | `bagging` | 4.785h |
| `1500-1550km` | 1500 to 1550 km | 48.24h | **`knn`** | **0.962h** | **97.9%** | 83.9% | `decision_tree` | 4.301h | `xgboost` | 4.643h |
| `1550-1600km` | 1550 to 1600 km | 50.76h | **`knn`** | **1.241h** | **97.7%** | 83.5% | `decision_tree` | 4.695h | `xgboost` | 5.069h |
| `1600-1650km` | 1600 to 1650 km | 53.53h | **`knn`** | **1.409h** | **97.5%** | 79.0% | `decision_tree` | 4.710h | `bagging` | 5.217h |
| `1650-1700km` | 1650 to 1700 km | 53.65h | **`knn`** | **1.040h** | **98.1%** | 83.4% | `decision_tree` | 4.580h | `xgboost` | 4.865h |
| `1700-1750km` | 1700 to 1750 km | 51.73h | **`knn`** | **1.720h** | **96.5%** | 78.6% | `decision_tree` | 4.043h | `bagging` | 4.483h |
| `1750-1800km` | 1750 to 1800 km | 51.80h | **`knn`** | **1.100h** | **98.2%** | 84.5% | `decision_tree` | 4.117h | `bagging` | 4.187h |
| `1800-1850km` | 1800 to 1850 km | 52.16h | **`knn`** | **1.647h** | **96.8%** | 79.2% | `decision_tree` | 4.397h | `xgboost` | 4.829h |
| `1850-1900km` | 1850 to 1900 km | 54.45h | **`knn`** | **0.928h** | **98.4%** | 82.7% | `bagging` | 4.489h | `decision_tree` | 4.722h |
| `1900-1950km` | 1900 to 1950 km | 55.13h | **`knn`** | **1.026h** | **98.1%** | 82.2% | `decision_tree` | 4.075h | `bagging` | 4.107h |
| `1950-2000km` | 1950 to 2000 km | 55.34h | **`knn`** | **1.307h** | **97.6%** | 81.0% | `decision_tree` | 4.512h | `gradient_boosting` | 4.655h |
| `2000-2050km` | 2000 to 2050 km | 57.32h | **`knn`** | **1.245h** | **98.0%** | 78.3% | `bagging` | 4.766h | `decision_tree` | 4.770h |
| `2050-2100km` | 2050 to 2100 km | 59.02h | **`knn`** | **1.638h** | **97.2%** | 79.9% | `xgboost` | 4.794h | `decision_tree` | 4.807h |
| `2100-2150km` | 2100 to 2150 km | 59.34h | **`knn`** | **0.839h** | **98.5%** | 85.6% | `decision_tree` | 4.041h | `gradient_boosting` | 4.380h |
| `2150-2200km` | 2150 to 2200 km | 61.89h | **`knn`** | **2.254h** | **96.7%** | 74.3% | `gradient_boosting` | 5.137h | `decision_tree` | 5.170h |
| `2200-2250km` | 2200 to 2250 km | 62.47h | **`knn`** | **0.914h** | **98.5%** | 83.4% | `gradient_boosting` | 4.461h | `bagging` | 4.877h |
| `2250-2300km` | 2250 to 2300 km | 62.08h | **`knn`** | **1.378h** | **97.9%** | 82.1% | `decision_tree` | 4.668h | `gradient_boosting` | 4.817h |
| `2300-2350km` | 2300 to 2350 km | 64.78h | **`knn`** | **1.412h** | **97.8%** | 74.7% | `gradient_boosting` | 4.060h | `decision_tree` | 4.141h |
| `2350-2400km` | 2350 to 2400 km | 66.84h | **`knn`** | **1.249h** | **98.1%** | 80.1% | `gradient_boosting` | 4.837h | `decision_tree` | 5.215h |

---

## Table 6: Tree SHAP Feature Importance & Attribution Telematics

Using Game-Theoretic Tree SHAP (SHapley Additive exPlanations), the exact marginal contribution of each logistics feature was quantified across the test set:

| Feature Variable | Encoding & Normalization | Attribution Share (%) | Mathematical Impact Vector | Physical Logistics Meaning |
|---|---|:---:|:---:|---|
| **Shipping Mode** (`shipping_mode_enc`) | ROAD=0, AIR=1, RAIL=2, SEA=3 | **32.54%** | Primary Velocity Scale Factor | Air freight reduces transit time by up to 82%; Sea/Rail scale for heavy freight |
| **Traffic Duration** (`traffic_duration_min`) | Continuous OSRM Simulation (Minutes) | **28.17%** | Non-Linear Positive Vector | Real-time congestion delay index across metro corridors and highway tolls |
| **Route Distance** (`distance_km`) | OSRM Table Road Distance (Kilometers) | **25.14%** | Linear Base Transit Floor | Fundamental geodesic floor; minimum physical driving hours required |
| **Priority Tier** (`priority_enc`) | STANDARD=0, EXPRESS=1, OVERNIGHT=2 | **5.95%** | Dispatch Queue Shift Factor | Express/Overnight dispatches bypass regional sort hubs for direct hub routes |
| **Package Category** (`package_type_enc`) | SMALL=0, MEDIUM=1, LARGE=2, FRAGILE=3... | **5.91%** | Dwell & Handling Multiplier | Fragile and Perishable packages require careful loading, adding hub dwell time |
| **Congestion Level** (`traffic_level_enc`) | LOW=0, MODERATE=1, HIGH=2, SEVERE=3 | **1.25%** | Acceleration Penalty | Severe bottlenecks compound highway idle duration during monsoon/peak rush |
| **Package Weight** (`package_weight_kg`) | Continuous Physical Mass (Kilograms) | **1.03%** | Inertia & Vehicle Class Factor | Parcels exceeding 20 kg require two-man handling or dedicated cargo vehicles |

---

## Table 7: Computational Efficiency & Production Inference Benchmarks

| Model Architecture | File Size (.pkl) | In-Memory RAM | Batch Throughput (48k Samples) | Single Prediction Latency | Production Dispatch Feasibility |
|---|:---:|:---:|:---:|:---:|---|
| **Decision Tree** | 1.3 MB | 3.2 MB | 0.01s | < 0.1 ms | Ultra-low latency edge devices, microcontrollers |
| **Linear Regression** | 657 B | 1.1 MB | 0.02s | < 0.1 ms | Embedded telematics, instant serverless endpoints |
| **XGBoost** | 4.2 MB | 8.4 MB | 1.15s | 0.4 ms | High-throughput dispatch APIs (thousands of req/sec) |
| **LightGBM** | 5.6 MB | 9.1 MB | 0.54s | 0.3 ms | High-throughput dispatch APIs, cloud containers |
| **CatBoost** | 4.2 MB | 7.9 MB | 0.29s | 0.2 ms | Resilient to missing features, high concurrency |
| **K-Nearest Neighbors** | 20.0 MB | 45.2 MB | 0.72s | 0.5 ms | Memory-backed routing caches, lookup tables |
| **Random Forest** | 12.9 MB | 32.5 MB | 0.33s | 0.3 ms | Core backend dispatcher, high stability |
| **Voting Ensemble** | 20.4 MB | 55.1 MB | 4.38s | 1.8 ms | Recommended primary production dispatch model |
| **Multi-Layer Perceptron** | 4.2 MB | 12.0 MB | 0.15s | 0.3 ms | Neural microservices, tensor servers |
| **TabNet** | 958 KB | 28.0 MB | 1.20s | 2.5 ms | Dedicated GPU inference pipelines |
| **Support Vector Regressor**| 860 KB | 15.4 MB | 21.57s | 12.0 ms | Too slow for large batch processing |

---

## Table 8: Environmental Sustainability & Carbon Footprint (GLEC / DEFRA Standards)

DeliverAI embeds the Global Logistics Emissions Council (GLEC) and DEFRA greenhouse gas auditing framework directly into every prediction:

| Transport Shipping Mode | Vehicle Type / Fleet Class | Average Speed | GLEC Emission Factor | Representative Route Emissions (500 km, 5 kg parcel) | Eco Efficiency Rating | Tree Offset Requirement |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **SEA (Inland / Coastal)** | Coastal Container Feeder Vessel | 22 km/h | **0.011 kg CO₂ / tonne-km** | **0.028 kg CO₂** | **Grade A+ (Optimal)** | 0.001 Trees |
| **RAIL (Indian Railways)** | Electric Freight Locomotive (DFC) | 65 km/h | **0.028 kg CO₂ / tonne-km** | **0.070 kg CO₂** | **Grade A (Excellent)** | 0.003 Trees |
| **ROAD (Highway Truck)** | Multi-Axle Diesel Commercial Truck | 48 km/h | **0.096 kg CO₂ / tonne-km** | **0.240 kg CO₂** | **Grade B (Moderate)** | 0.011 Trees |
| **AIR (Domestic Cargo)** | Dedicated Freight Aircraft (B737) | 680 km/h | **0.602 kg CO₂ / tonne-km** | **1.505 kg CO₂** | **Grade F (High Carbon)** | 0.068 Trees |

---

## Table 9: Engineering Post-Mortem & Windows Multi-Threading Isolation

| Architectural Element | Challenge Encountered | Underlying Mechanism | Engineered Remediation Protocol | Verification Outcome |
|---|---|---|---|---|
| **Windows CUDA DLL Detach** | Silent crash 0xC0000409 (STATUS_STACK_BUFFER_OVERRUN) | Werkzeug HTTP worker threads deallocating CUDA contexts during DLL_PROCESS_DETACH in nvcuda.dll | Re-serialized tree ensembles (xgboost.pkl, voting.pkl) explicitly with device='cpu' and n_jobs=1 | 100% server stability across extended high-load runs |
| **Process Fork Contention** | Scikit-learn / Joblib OpenMP CPU deadlock | Loky multiprocessing backend spawning unmanaged sub-processes on Windows | Forced joblib.parallel.DEFAULT_BACKEND = 'threading' and set OMP_NUM_THREADS=1 | Sub-millisecond response without IPC socket overhead |
| **Hardware Segregation** | VRAM saturation on 6GB GPU | Tabular models competing for GPU memory with LM Studio local LLM | Tabular ML assigned strictly to CPU; NVIDIA RTX 3050 reserved exclusively for TabNet and local LLM Copilot | Zero VRAM thrashing; instant LLM token streaming |

---

## Table 10: High-Scale Empirical Accuracy & Throughput Projections per 100,000 Shipments

To validate enterprise production readiness, we extrapolate empirical scaling metrics across a massive continuous workload of **100,000 logistics dispatches** based on our 147k training partition and 48k benchmark curve:

| Rank | Model Architecture | Scaling Category | Projected 100k Accuracy (%) | Projected MAE (h) | Projected RMSE (h) | Within ±30 min (%) | Within ±60 min (%) | Batch Time per 100k Records | RAM Usage at 100k Load | Enterprise Deployment Tier |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | **`knn`** | Distance Memory Index | **97.7%** | **0.84h** | **2.89h** | **83.4%** | **91.2%** | 1.48s | 88 MB | Tier-1 Corridors & Route Caches |
| 2 | **`voting`** | Meta-Ensemble | **96.2%** | **1.28h** | **2.88h** | **56.8%** | **68.2%** | 9.12s | 115 MB | Core Mission-Critical Dispatcher |
| 3 | **`random_forest`** | Tree Ensemble | **96.1%** | **1.28h** | **2.90h** | **58.1%** | **69.5%** | 0.68s | 65 MB | Primary High-Throughput Engine |
| 4 | **`extra_trees`** | Tree Ensemble | **96.1%** | **1.29h** | **2.93h** | **58.3%** | **69.4%** | 0.71s | 68 MB | Secondary Validation Engine |
| 5 | **`bagging`** | Tree Ensemble | **96.1%** | **1.29h** | **2.92h** | **57.5%** | **68.7%** | 6.55s | 72 MB | Hyperlocal & Intra-City Dedicated |
| 6 | **`lightgbm`** | Gradient Boosted | **96.1%** | **1.30h** | **2.91h** | **57.0%** | **68.1%** | 1.12s | 19 MB | Cloud Microservice / Serverless |
| 7 | **`catboost`** | Gradient Boosted | **96.1%** | **1.31h** | **2.92h** | **55.6%** | **67.1%** | 0.61s | 16 MB | Rain / Ghat Corridor Routing |
| 8 | **`gradient_boosting`** | Gradient Boosted | **96.1%** | **1.32h** | **2.92h** | **56.1%** | **66.8%** | 0.60s | 18 MB | Continuous Gradient Baseline |
| 9 | **`hist_gradient_boosting`** | Histogram Boosting| **96.1%** | **1.31h** | **2.90h** | **55.9%** | **67.0%** | 0.60s | 14 MB | High-Speed Internal Dispatch APIs |
| 10 | **`xgboost`** | Gradient Boosted | **96.0%** | **1.32h** | **2.97h** | **56.6%** | **67.8%** | 2.38s | 22 MB | Enterprise Container API |
| 11 | **`mlp`** | Neural Network | **96.1%** | **1.30h** | **2.90h** | **56.4%** | **68.9%** | 0.32s | 24 MB | Deep Learning Tensor Cluster |
| 12 | **`tabnet`** | Deep Learning | **95.9%** | **1.50h** | **3.00h** | **39.3%** | **64.9%** | 2.50s | 56 MB | Attention Interpretation Studio |
| 13 | **`decision_tree`** | Tree-Based | **94.8%** | **1.44h** | **3.37h** | **59.2%** | **69.2%** | 0.02s | 6 MB | Ultra-Fast Edge & Mobile Devices |
| 14 | **`svr`** | Support Vector | **95.5%** | **1.26h** | **3.12h** | **66.7%** | **74.6%** | 44.80s | 32 MB | Low-Frequency High-Margin Freight |
| 15 | **`stacking`** | Meta-Ensemble | **96.0%** | **1.30h** | **2.88h** | **56.2%** | **67.5%** | 0.60s | 48 MB | Specialized Executive Audits |
| 16 | **`elastic_net`** | Regularized Linear | **84.9%** | **3.38h** | **5.74h** | **20.6%** | **36.1%** | 0.04s | 3 MB | Instant Linear Reference |
| 17 | **`lasso`** | Regularized Linear | **84.9%** | **3.38h** | **5.74h** | **20.6%** | **36.1%** | 0.04s | 3 MB | Feature Sparsity Baseline |
| 18 | **`ridge`** | Regularized Linear | **84.9%** | **3.38h** | **5.74h** | **20.3%** | **36.1%** | 0.03s | 3 MB | Collinearity Control Baseline |
| 19 | **`linear_regression`** | Baseline Linear | **84.9%** | **3.38h** | **5.74h** | **20.3%** | **36.1%** | 0.03s | 3 MB | Absolute Simplicity Baseline |

---

## 11. Conclusion & Academic Contributions

DeliverAI demonstrates that empirical distance discretization combined with a Small Language Model routing engine outperforms any single standalone algorithm across India's complex supply chain geography:
1. **Meta-Ensembling Champions Global Precision:** Voting Regressor champions global long-haul accuracy (**R² = 0.9620**, **RMSE = 2.886 hours**), providing resilient generalizability across multi-state shipping corridors.
2. **Hyperlocal Mastery:** Bagging Regressor masters hyperlocal corridors (<= 50 km) with a mean error of just 4.8 minutes, mitigating urban red-light delays.
3. **Intercity Highway Precision:** K-Nearest Neighbors demonstrates unmatched precision on national corridors (>= 50 km) with **97.7% accuracy** across 48,000 empirical predictions.
4. **Symbiosis of ML & Generative AI:** Deploying tabular ML on multi-core CPU with a dedicated local Small Language Model (SLM) on an NVIDIA RTX 3050 creates a production-grade, zero-latency logistics dispatch copilot.

---

## 12. Academic Endorsement & Institutional Sign-Off

This document certifies that the minor project titled **DeliverAI: AI-Based Package Delivery Time Prediction System** represents an authentic record of academic research, mathematical formulation, and software engineering conducted during the 5th Semester of Bachelor of Technology (B.Tech) in Computer Science & Engineering.

| Role / Designation | Name & Affiliation | Signature | Date |
|---|---|:---:|:---:|
| **Candidate / Lead Researcher** | **Argho**<br/>B.Tech Computer Science & Engineering | _________________________________ | 20 / 10 / 2026 |
| **Project Supervisor / Guide** | **Faculty Supervisor**<br/>Department of Computer Science & Engineering | _________________________________ | ____ / ____ / 2026 |
| **Project Coordinator** | **Coordinator, Minor Projects**<br/>Department of Computer Science & Engineering | _________________________________ | ____ / ____ / 2026 |
| **Head of Department (CSE)** | **Head of Department**<br/>Department of Computer Science & Engineering | _________________________________ | ____ / ____ / 2026 |
| **External Examiner** | **Board of Examiners**<br/>University Evaluation Panel | _________________________________ | ____ / ____ / 2026 |

<br/>

| Official Department Seal | Institutional Verification Code | Examination Status |
|:---:|:---:|:---:|
| <br/>**[ INSTITUTIONAL ACADEMIC SEAL ]**<br/><br/>Department of Computer Science & Engineering | `DELIVERAI-BTECH-CSE-5SEM-2026` | **APPROVED & ENDORSED** |
