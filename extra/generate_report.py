"""
generate_report.py
==============================================================================
Generates a comprehensive, publication-grade academic project report for
DeliverAI (5th Semester B.Tech Minor Project / Research Monograph) in both
Markdown and PDF formats.

Includes:
- 184,029 unified records across 8 Indian logistics sources
- 19-Model ML/DL empirical benchmarks
- 25km interval discretization analysis (96 geographic tiers)
- Local Small Language Model (SLM) route & leg-by-leg routing engine
- Hardware-accelerated Local AI Copilot Studio (NVIDIA RTX 3050 CUDA 12.4)
- Tree SHAP Explainable AI & GLEC/DEFRA Green Logistics
- Reconstructed Executive Command Center architecture
- Windows CUDA 0xC0000409 engineering post-mortem
==============================================================================
"""

import os
import sys
import subprocess
import shutil

# ── Auto-forward to project venv if invoked from system Python ───
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    _res = subprocess.run([_venv_python] + sys.argv)
    sys.exit(_res.returncode)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DeliverAI: AI-Based Package Delivery Time Prediction System</title>
<style>
  @page {
    size: A4;
    margin: 18mm 14mm 18mm 14mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 8pt;
      color: #64748b;
    }
    @bottom-left {
      content: "DeliverAI · B.Tech CSE 5th Sem Minor Project";
      font-size: 8pt;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Plus Jakarta Sans", Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
  }

  .page-break {
    page-break-after: always;
  }

  /* Cover Page */
  .cover {
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    padding: 25px 15px;
  }

  .cover-header {
    border-bottom: 3px solid #2563eb;
    padding-bottom: 18px;
  }

  .institution {
    font-size: 13pt;
    font-weight: 800;
    color: #1e3a8a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
  }

  .department {
    font-size: 10.5pt;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }

  .project-title {
    font-size: 23pt;
    font-weight: 800;
    color: #0f172a;
    margin: 30px 0 10px 0;
    line-height: 1.25;
    letter-spacing: -0.5px;
  }

  .project-subtitle {
    font-size: 11.5pt;
    color: #2563eb;
    font-weight: 600;
    margin-bottom: 24px;
    line-height: 1.45;
  }

  .badge-container {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 25px;
  }

  .badge {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 8.5pt;
    font-weight: 700;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
  }

  .badge-green {
    background: #ecfdf5;
    color: #047857;
    border-color: #a7f3d0;
  }

  .badge-purple {
    background: #faf5ff;
    color: #7e22ce;
    border-color: #e9d5ff;
  }

  .meta-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 16px 20px;
    text-align: left;
    max-width: 540px;
    margin: 0 auto 20px auto;
    font-size: 9.5pt;
  }

  .meta-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dashed #e2e8f0;
  }
  .meta-row:last-child {
    border-bottom: none;
  }

  .meta-label {
    font-weight: 700;
    color: #475569;
  }

  .cover-footer {
    border-top: 1px solid #cbd5e1;
    padding-top: 12px;
    font-size: 8.5pt;
    color: #64748b;
  }

  /* Content Headings */
  h1 {
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 5px;
    margin-top: 24px;
    margin-bottom: 12px;
  }

  h2 {
    font-size: 12pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-top: 20px;
    margin-bottom: 8px;
  }

  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 15px;
    margin-bottom: 6px;
  }

  p {
    margin: 7px 0;
    text-align: justify;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9pt;
  }

  th, td {
    padding: 6px 8px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }

  th {
    background-color: #f1f5f9;
    font-weight: 700;
    color: #0f172a;
  }

  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  .text-right { text-align: right; }
  .text-center { text-align: center; }
  .highlight { font-weight: 700; color: #2563eb; }

  .winner-tag {
    background: #dbeafe;
    color: #1e40af;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 8pt;
  }

  /* Callout Boxes */
  .callout {
    border-left: 4px solid #2563eb;
    background: #eff6ff;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    margin: 12px 0;
    font-size: 9.5pt;
  }

  .callout-title {
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 3px;
  }

  .callout-success {
    border-left-color: #10b981;
    background: #ecfdf5;
  }
  .callout-success .callout-title {
    color: #047857;
  }

  /* Code & Architecture */
  pre {
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 12px;
    border-radius: 6px;
    font-size: 8pt;
    font-family: Consolas, "JetBrains Mono", monospace;
    overflow-x: auto;
    margin: 10px 0;
    line-height: 1.4;
  }

  code {
    font-family: Consolas, "JetBrains Mono", monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0f172a;
  }

  pre code {
    background: transparent;
    padding: 0;
    color: inherit;
  }

  ul, ol {
    margin: 5px 0 10px 18px;
    padding: 0;
  }
  li {
    margin-bottom: 3px;
  }

  .arch-box {
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    border-radius: 6px;
    padding: 10px;
    font-family: Consolas, monospace;
    font-size: 8pt;
    white-space: pre;
    line-height: 1.35;
    margin: 12px 0;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="cover-header">
    <div class="institution">Academic Project Report &amp; Research Monograph</div>
    <div class="department">Department of Computer Science &amp; Engineering · 5th Semester B.Tech Minor Project</div>
  </div>

  <div>
    <div class="project-title">DeliverAI: AI-Based Package Delivery Time Prediction System</div>
    <div class="project-subtitle">
      Empirical Benchmark of 19 Machine Learning &amp; Deep Learning Regression Models across 184,000+ Inland India Logistics Records, Local Small Language Model (SLM) Route Decision Routing, and Dedicated Hardware-Accelerated Copilot
    </div>
    
    <div class="badge-container">
      <span class="badge">184,029 Records</span>
      <span class="badge">19 ML/DL Architectures</span>
      <span class="badge">96 Distance Tiers (25km)</span>
      <span class="badge-green">Champion R² = 0.9624</span>
      <span class="badge-purple">Local SLM Engine (Llama 3.2 3B)</span>
      <span class="badge">NVIDIA RTX 3050 CUDA 12.4</span>
      <span class="badge-green">Tree SHAP Explainability</span>
    </div>

    <div class="meta-box">
      <div class="meta-row"><span class="meta-label">Project Title:</span> <span>DeliverAI Package Delivery Time Predictor</span></div>
      <div class="meta-row"><span class="meta-label">Academic Level:</span> <span>B.Tech CSE — 5th Semester Minor Project</span></div>
      <div class="meta-row"><span class="meta-label">Domain:</span> <span>Applied Artificial Intelligence, Machine Learning &amp; Logistics Telematics</span></div>
      <div class="meta-row"><span class="meta-label">Evaluation Date:</span> <span>October 2026</span></div>
      <div class="meta-row"><span class="meta-label">Software Stack:</span> <span>Python 3.12 · PyTorch 2.5.1 · Scikit-Learn · Flask · Leaflet</span></div>
      <div class="meta-row"><span class="meta-label">Hardware Acceleration:</span> <span>NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4)</span></div>
      <div class="meta-row"><span class="meta-label">Local LLM Server:</span> <span>LM Studio (Port 1234 / OpenAI-Compatible v1 API)</span></div>
      <div class="meta-row"><span class="meta-label">Geospatial Routing:</span> <span>OSRM Ground Table Engine &amp; OpenWeather Precipitation</span></div>
    </div>
  </div>

  <div class="cover-footer">
    Empirical research benchmarked across 8 inland transportation repositories: Delhivery Courier, Amazon India Fulfillment, Hyperlocal Trips, Bangalore Traffic Corridors, Indian Highways, and Indian Railways Freight.
  </div>
</div>

<div class="page-break"></div>

<!-- ABSTRACT -->
<h1>Abstract</h1>
<p>
Predicting accurate transit duration for freight logistics across the Indian subcontinent represents an intricate geospatial and algorithmic challenge. Inland transportation in India is influenced by severe highway traffic bottlenecks, heterogeneous vehicle categories (from two-wheeler hyperlocal delivery to multi-axle freight containers and railway freight), monsoon-induced route diversions, and seasonal festive surges (e.g., Diwali, Durga Puja). This project presents <strong>DeliverAI</strong>, an end-to-end intelligent logistics decision-support platform trained on a massive, unified dataset of <strong>184,029 authentic shipment records</strong> compiled from 8 distinct Indian transportation repositories.
</p>
<p>
We conduct an exhaustive empirical benchmark of <strong>19 distinct regression architectures</strong>, spanning regularized linear baselines (Ridge, Lasso, Elastic Net), tree-based ensembles (Random Forest, Extra Trees, Decision Tree, Bagging), gradient-boosted trees (XGBoost, LightGBM, CatBoost, HistGradientBoosting, Gradient Boosting), distance-based estimators (K-Nearest Neighbors, Support Vector Regression), deep learning architectures (Multi-Layer Perceptron, PyTorch TabNet), and meta-ensembles (Stacking Regressor, Voting Regressor).
</p>
<p>
On a rigorous 20% holdout test partition of <strong>36,806 shipments</strong>, the <strong>Voting Regressor</strong> achieved the overall champion performance with an <strong>R² score of 0.9624</strong>, Root Mean Squared Error (RMSE) of <strong>2.873 hours</strong>, and Mean Absolute Error (MAE) of <strong>1.290 hours</strong>. Furthermore, a systematic 25km interval discretization benchmark across 96 geographic tiers (0 km to 2,400 km) revealed that <strong>Bagging Regressor</strong> dominates hyperlocal/urban routes (&le; 25 km) with an MAE of 0.080 hours (~4.8 minutes), while <strong>K-Nearest Neighbors (KNN)</strong> demonstrates unmatched precision on intercity and national corridors (&ge; 25 km) with 97.7% accuracy.
</p>
<p>
Expanding beyond static predictions, DeliverAI integrates a <strong>Small Language Model (SLM) Route Decision Engine</strong> running locally on an <strong>NVIDIA GeForce RTX 3050 6GB GPU</strong> via LM Studio. The SLM decomposes route corridors into 25km intervals, evaluates weather friction, and dynamically allocates specialized algorithms per leg. The platform features an executive dark obsidian glassmorphism UI, game-theoretic Tree SHAP explainability, and GLEC/DEFRA freight carbon footprint auditing.
</p>

<!-- SECTION 1: INTRODUCTION -->
<h1>1. Introduction &amp; Problem Statement</h1>
<p>
Logistics and supply chain fulfillment in India account for approximately 13–14% of the nation's Gross Domestic Product (GDP), significantly higher than the global benchmark of 8%. A primary contributor to this inefficiency is unpredictable transit time estimation. Unlike North American or European logistics corridors characterized by uniform road infrastructure and predictable highway traffic, Indian inland logistics operates across extreme operational diversity:
</p>
<ul>
  <li><strong>Infrastructure Heterogeneity:</strong> Golden Quadrilateral expressways intersect with single-lane state highways, railway level crossings, and municipal roads.</li>
  <li><strong>Multi-Modal Transport Modes:</strong> Shipments transition across Road (trucks and vans), Air (expedited cargo), Rail (Dedicated Freight Corridors), and Hyperlocal two-wheelers.</li>
  <li><strong>Traffic Bottlenecks:</strong> Metropolitan intersections (e.g., Bangalore Silk Board, Mumbai Western Express Highway, Delhi NCR bypasses) create non-linear delays that cannot be modeled by simple linear velocity equations.</li>
  <li><strong>Environmental &amp; Seasonal Surges:</strong> Monsoonal precipitation (July–September) introduces 15–35% transit delays, while festive shopping peaks (October–November) overwhelm hub processing capacities.</li>
</ul>

<div class="callout">
  <div class="callout-title">DeliverAI Core Research Objective</div>
  To design, clean, unify, and benchmark 19 AI/ML architectures on real Indian logistics data, deploying a dynamic distance-stratified and Local Small Language Model (SLM) routing mechanism that automatically dispatches the mathematically optimal model for any given route length, weather condition, and highway leg.
</div>

<!-- SECTION 2: DATASET ENGINEERING -->
<h1>2. Multi-Source Dataset Architecture &amp; Ingestion</h1>
<p>
To prevent synthetic bias and capture authentic transit realities, DeliverAI merges and harmonizes <strong>8 heterogeneous data sources</strong> spanning national courier corridors, e-commerce retail fulfillment, intra-city two-wheeler deliveries, metro traffic telemetry, and railway freight schedules:
</p>

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Dataset / Repository Source</th>
      <th class="text-right">Records</th>
      <th>Primary Logistics Domain</th>
      <th>Key Features Extracted</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td><strong>Delhivery Logistics Dataset</strong></td>
      <td class="text-right">55,000</td>
      <td>National Courier &amp; Truck Freight</td>
      <td>Actual transit duration, OSRM distance, FTL vs Carting mode, route segment times.</td>
    </tr>
    <tr>
      <td>2</td>
      <td><strong>Amazon India Sales &amp; Shipping</strong></td>
      <td class="text-right">25,000</td>
      <td>B2C E-Commerce Retail Fulfillment</td>
      <td>Expedited vs standard shipping, apparel/electronics parcels, domestic fulfillment centers.</td>
    </tr>
    <tr>
      <td>3</td>
      <td><strong>Hyperlocal Food &amp; Parcel Trips</strong></td>
      <td class="text-right">45,593</td>
      <td>Urban Two-Wheeler Rapid Transit</td>
      <td>High traffic sensitivity, delivery agent ratings, rapid urban turnaround times (&lt; 25 km).</td>
    </tr>
    <tr>
      <td>4</td>
      <td><strong>Bangalore City Traffic Corridors</strong></td>
      <td class="text-right">8,936</td>
      <td>Metro Intersection Telemetry</td>
      <td>Peak-hour congestion ratios, signal delay buffers, weather congestion interaction.</td>
    </tr>
    <tr>
      <td>5</td>
      <td><strong>Indian Road Corridors &amp; Hazards</strong></td>
      <td class="text-right">20,000</td>
      <td>Highway Speed &amp; Safety Bottlenecks</td>
      <td>National Highway (NH) vs State Highway (SH) condition factors, terrain restrictions.</td>
    </tr>
    <tr>
      <td>6</td>
      <td><strong>Indian Railways Freight &amp; Cargo</strong></td>
      <td class="text-right">10,000</td>
      <td>Bulk Container &amp; Heavy Rail Transit</td>
      <td>DFC track corridor distances, yard marshaling delays, hub dwell intervals.</td>
    </tr>
    <tr>
      <td>7</td>
      <td><strong>Flipkart E-Commerce Orders</strong></td>
      <td class="text-right">1,500</td>
      <td>Multi-Item Consumer Shipments</td>
      <td>Item quantity multipliers, dimensional package weights, regional hub dispatches.</td>
    </tr>
    <tr>
      <td>8</td>
      <td><strong>IMD Weather &amp; Festival Surge Layer</strong></td>
      <td class="text-right">18,000</td>
      <td>Climatic &amp; Seasonal Impact Matrix</td>
      <td>Monsoon precipitation delays (15–35%), Diwali/Holi festive delivery capacity surges.</td>
    </tr>
    <tr style="background:#f1f5f9; font-weight:700;">
      <td colspan="2"><strong>Consolidated Total Dataset</strong></td>
      <td class="text-right"><strong>184,029</strong></td>
      <td colspan="2"><strong>Complete Inland India Multimodal Supply Chain Representation</strong></td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 3: DATA PREPROCESSING -->
<h1>3. Data Cleaning &amp; Preprocessing Methodology</h1>
<p>
Raw logistics telemetry suffers from sensor drops, timestamp inconsistencies, differing schema nomenclatures, and manual dispatch errors. We engineered an automated, robust data cleaning pipeline in <code>backend/data/process_datasets.py</code>:
</p>

<h3>Phase 1: Schema Unification &amp; Normalization</h3>
<pre><code>TARGET_SCHEMA = [
    'tracking_id',          # Standardized alphanumeric ID (e.g., DLV000001, AMZ000001)
    'origin_city',          # Origin hub geocode
    'destination_city',     # Destination hub geocode
    'distance_km',          # Great-circle & OSRM ground road distance (km)
    'traffic_duration_min', # Simulated & telemetry-adjusted traffic time (min)
    'traffic_level_enc',    # Ordinal encoding: LOW=0, MODERATE=1, HIGH=2, SEVERE=3
    'package_weight_kg',    # Calibrated parcel weight (0.1 kg to 2,500 kg)
    'package_type_enc',     # SMALL=0, MEDIUM=1, LARGE=2, FRAGILE=3, PERISHABLE=4
    'priority_enc',         # STANDARD=0, EXPRESS=1, OVERNIGHT=2
    'shipping_mode_enc',    # ROAD=0, AIR=1, RAIL=2, SEA=3
    'actual_time_hours',    # Target continuous ground truth delivery time (hours)
    'source'                # Data lineage provenance tag
]</code></pre>

<h3>Phase 2: Missing Value Imputation</h3>
<ul>
  <li><strong>Geographic Distance:</strong> Where coordinates were absent, city pairs were resolved via Nominatim Geocoding and OSRM Table routing. Fallback distances utilized haversine formulas adjusted with a 1.28x Indian highway winding factor.</li>
  <li><strong>Traffic Duration:</strong> Missing congestion durations were reconstructed by multiplying road distance by baseline highway speeds (45 km/h for heavy trucks, 35 km/h for city vans, 25 km/h for hyperlocal bikes) combined with the Bangalore traffic congestion ratio.</li>
  <li><strong>Categorical Attributes:</strong> Unspecified shipping modes were imputed to <code>ROAD</code> (representing 74% of domestic Indian freight), priority defaulted to <code>STANDARD</code>, and package type to <code>MEDIUM</code>.</li>
</ul>

<h3>Phase 3: Outlier Truncation &amp; Physical Speed Bounds</h3>
<ul>
  <li><code>actual_time_hours</code> must strictly satisfy: $0.15\text{ h} \le \text{actual\_time\_hours} \le 168.0\text{ h}$ (7 days).</li>
  <li><code>distance_km</code> must satisfy: $1.0\text{ km} \le \text{distance\_km} \le 3,500.0\text{ km}$ (Kashmir to Kanyakumari span).</li>
  <li><strong>Implied Velocity Sanity Check:</strong> Shipments with implied road speed $> 110\text{ km/h}$ were re-routed to <code>AIR</code> mode or truncated. Shipments with implied speed $< 4\text{ km/h}$ were verified against seasonal flood records or discarded as abandoned orders.</li>
</ul>

<h3>Phase 4: Standardization &amp; Data Leakage Prevention</h3>
<p>
The dataset was partitioned into an <strong>80% Training Set (147,223 samples)</strong> and a <strong>20% Test Set (36,806 samples)</strong>. A <code>StandardScaler</code> was fitted strictly on the training partition and serialized to <code>backend/models/saved/scaler.pkl</code>:
$$\mu = \frac{1}{N}\sum_{i=1}^N X_{i,\text{train}}, \quad \sigma = \sqrt{\frac{1}{N}\sum_{i=1}^N (X_{i,\text{train}} - \mu)^2}, \quad X_{\text{scaled}} = \frac{X - \mu}{\sigma}$$
</p>

<!-- SECTION 4: THE 19 MACHINE LEARNING MODELS -->
<h1>4. Model Architectures &amp; Algorithmic Design</h1>
<p>
DeliverAI implemented, trained, and evaluated <strong>19 distinct regression architectures</strong> categorized into 6 theoretical families:
</p>

<table>
  <thead>
    <tr>
      <th>Family</th>
      <th>Model Name</th>
      <th>Mathematical Foundation / Loss Function</th>
      <th>Key Hyperparameters</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="4"><strong>Linear Baselines</strong></td>
      <td><strong>Linear Regression</strong></td>
      <td>Ordinary Least Squares: $\min_{\mathbf{w}} \|\mathbf{y} - \mathbf{X}\mathbf{w}\|_2^2$</td>
      <td><code>fit_intercept=True</code></td>
    </tr>
    <tr>
      <td><strong>Ridge Regression</strong></td>
      <td>$L_2$ Regularization: $\min_{\mathbf{w}} \|\mathbf{y} - \mathbf{X}\mathbf{w}\|_2^2 + \alpha \|\mathbf{w}\|_2^2$</td>
      <td><code>alpha=1.0</code></td>
    </tr>
    <tr>
      <td><strong>Lasso Regression</strong></td>
      <td>$L_1$ Regularization: $\min_{\mathbf{w}} \|\mathbf{y} - \mathbf{X}\mathbf{w}\|_2^2 + \alpha \|\mathbf{w}\|_1$</td>
      <td><code>alpha=0.1, max_iter=2000</code></td>
    </tr>
    <tr>
      <td><strong>Elastic Net</strong></td>
      <td>Convex combination: $\min_{\mathbf{w}} \|\mathbf{y} - \mathbf{X}\mathbf{w}\|_2^2 + \alpha \rho \|\mathbf{w}\|_1 + \frac{\alpha(1-\rho)}{2}\|\mathbf{w}\|_2^2$</td>
      <td><code>alpha=0.1, l1_ratio=0.5</code></td>
    </tr>
    <tr>
      <td rowspan="4"><strong>Tree Ensembles</strong></td>
      <td><strong>Decision Tree</strong></td>
      <td>Greedy recursive variance reduction splitting (CART)</td>
      <td><code>max_depth=16, min_samples_split=5</code></td>
    </tr>
    <tr>
      <td><strong>Random Forest</strong></td>
      <td>Bootstrap Aggregation of de-correlated trees with random feature subsampling</td>
      <td><code>n_estimators=100, max_depth=18, n_jobs=1</code></td>
    </tr>
    <tr>
      <td><strong>Extra Trees</strong></td>
      <td>Extremely Randomized Trees; draws random thresholds for candidate features</td>
      <td><code>n_estimators=100, max_depth=18, n_jobs=1</code></td>
    </tr>
    <tr>
      <td><strong>Bagging Regressor</strong></td>
      <td>Ensemble of sub-estimators trained on random subsets of training samples</td>
      <td><code>n_estimators=50, max_samples=0.85</code></td>
    </tr>
    <tr>
      <td rowspan="5"><strong>Gradient Boosting</strong></td>
      <td><strong>Gradient Boosting</strong></td>
      <td>Sequential additive trees minimizing squared error via gradient descent</td>
      <td><code>n_estimators=150, learning_rate=0.1, max_depth=6</code></td>
    </tr>
    <tr>
      <td><strong>HistGradientBoosting</strong></td>
      <td>Histogram-based binning of continuous features into integer bins ($O(N)$)</td>
      <td><code>max_iter=150, max_depth=8</code></td>
    </tr>
    <tr>
      <td><strong>XGBoost</strong></td>
      <td>Exact/approximate greedy tree search with 2nd-order Taylor loss expansion</td>
      <td><code>n_estimators=150, learning_rate=0.08, max_depth=6, device='cpu'</code></td>
    </tr>
    <tr>
      <td><strong>LightGBM</strong></td>
      <td>Leaf-wise tree growth with Gradient-based One-Side Sampling (GOSS)</td>
      <td><code>n_estimators=150, learning_rate=0.08, num_leaves=31</code></td>
    </tr>
    <tr>
      <td><strong>CatBoost</strong></td>
      <td>Ordered boosting with oblivious symmetric decision trees and target statistics</td>
      <td><code>iterations=200, learning_rate=0.08, depth=6</code></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Distance / Kernel</strong></td>
      <td><strong>K-Nearest Neighbors</strong></td>
      <td>Euclidean distance instance-based retrieval: $\hat{y} = \frac{1}{k}\sum_{i \in N_k} y_i$</td>
      <td><code>n_neighbors=7, weights='distance', metric='euclidean'</code></td>
    </tr>
    <tr>
      <td><strong>Support Vector (SVR)</strong></td>
      <td>Radial Basis Function (RBF) kernel with $\epsilon$-insensitive margin</td>
      <td><code>kernel='rbf', C=10.0, epsilon=0.1</code></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Deep Learning</strong></td>
      <td><strong>Multi-Layer Perceptron</strong></td>
      <td>Feedforward neural network with Adam optimizer and ReLU activation</td>
      <td><code>hidden_layer_sizes=(128, 64, 32), max_iter=250</code></td>
    </tr>
    <tr>
      <td><strong>PyTorch TabNet</strong></td>
      <td>Attentive sequential transformer with sparse feature selection masks</td>
      <td><code>n_d=16, n_a=16, n_steps=4, gamma=1.3, batch_size=1024</code></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Meta Ensembles</strong></td>
      <td><strong>Stacking Regressor</strong></td>
      <td>2-stage stacking: CatBoost, LightGBM, GradientBoosting with Ridge meta-learner</td>
      <td><code>cv=5, final_estimator=Ridge()</code></td>
    </tr>
    <tr>
      <td><strong>Voting Regressor</strong></td>
      <td>Uniform soft-averaging ensemble of CatBoost, LightGBM, XGBoost, and Random Forest</td>
      <td><code>weights=[1, 1, 1, 1]</code></td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 5: BENCHMARK LEADERBOARD -->
<h1>5. Comprehensive 19-Model Holdout Benchmark</h1>
<p>
All 19 models were trained on <strong>147,223 training samples</strong> and evaluated on the independent <strong>36,806 holdout test samples</strong>:
</p>

<table>
  <thead>
    <tr>
      <th class="text-center">Rank</th>
      <th>Model Architecture</th>
      <th>Category</th>
      <th class="text-center">R² Score</th>
      <th class="text-center">RMSE (h)</th>
      <th class="text-center">MAE (h)</th>
      <th class="text-center">MAPE (%)</th>
      <th class="text-center">Tol &plusmn;30m</th>
      <th class="text-center">Training Time</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#dbeafe; font-weight:700;">
      <td class="text-center">🥇 1</td>
      <td><strong>Voting Regressor</strong></td>
      <td>Ensemble / Meta</td>
      <td class="text-center highlight">0.9624</td>
      <td class="text-center highlight">2.873h</td>
      <td class="text-center">1.290h</td>
      <td class="text-center">16.1%</td>
      <td class="text-center">56.5%</td>
      <td class="text-center">9.8s</td>
    </tr>
    <tr>
      <td class="text-center">🥈 2</td>
      <td><strong>Random Forest</strong></td>
      <td>Tree Ensemble</td>
      <td class="text-center">0.9623</td>
      <td class="text-center">2.877h</td>
      <td class="text-center highlight">1.281h</td>
      <td class="text-center">15.4%</td>
      <td class="text-center">56.8%</td>
      <td class="text-center">5.6s</td>
    </tr>
    <tr>
      <td class="text-center">🥉 3</td>
      <td><strong>Stacking Regressor</strong></td>
      <td>Ensemble / Meta</td>
      <td class="text-center">0.9622</td>
      <td class="text-center">2.879h</td>
      <td class="text-center">1.300h</td>
      <td class="text-center">16.5%</td>
      <td class="text-center">56.2%</td>
      <td class="text-center">95.2s</td>
    </tr>
    <tr>
      <td class="text-center">4</td>
      <td><strong>Extra Trees Regressor</strong></td>
      <td>Tree Ensemble</td>
      <td class="text-center">0.9622</td>
      <td class="text-center">2.880h</td>
      <td class="text-center">1.285h</td>
      <td class="text-center">15.1%</td>
      <td class="text-center">56.7%</td>
      <td class="text-center">3.7s</td>
    </tr>
    <tr>
      <td class="text-center">5</td>
      <td><strong>CatBoost Regressor</strong></td>
      <td>Gradient Boosting</td>
      <td class="text-center">0.9619</td>
      <td class="text-center">2.891h</td>
      <td class="text-center">1.309h</td>
      <td class="text-center">17.3%</td>
      <td class="text-center">55.7%</td>
      <td class="text-center">5.7s</td>
    </tr>
    <tr>
      <td class="text-center">6</td>
      <td><strong>LightGBM Regressor</strong></td>
      <td>Gradient Boosting</td>
      <td class="text-center">0.9619</td>
      <td class="text-center">2.892h</td>
      <td class="text-center">1.304h</td>
      <td class="text-center">16.5%</td>
      <td class="text-center">56.3%</td>
      <td class="text-center">1.0s</td>
    </tr>
    <tr>
      <td class="text-center">7</td>
      <td><strong>Bagging Regressor</strong></td>
      <td>Tree Ensemble</td>
      <td class="text-center">0.9615</td>
      <td class="text-center">2.906h</td>
      <td class="text-center">1.291h</td>
      <td class="text-center">14.3%</td>
      <td class="text-center">56.7%</td>
      <td class="text-center">4.5s</td>
    </tr>
    <tr>
      <td class="text-center">8</td>
      <td><strong>Hist Gradient Boosting</strong></td>
      <td>Gradient Boosting</td>
      <td class="text-center">0.9614</td>
      <td class="text-center">2.910h</td>
      <td class="text-center">1.318h</td>
      <td class="text-center">17.1%</td>
      <td class="text-center">55.9%</td>
      <td class="text-center">0.5s</td>
    </tr>
    <tr>
      <td class="text-center">9</td>
      <td><strong>Gradient Boosting</strong></td>
      <td>Gradient Boosting</td>
      <td class="text-center">0.9613</td>
      <td class="text-center">2.914h</td>
      <td class="text-center">1.321h</td>
      <td class="text-center">17.3%</td>
      <td class="text-center">56.1%</td>
      <td class="text-center">51.6s</td>
    </tr>
    <tr>
      <td class="text-center">10</td>
      <td><strong>XGBoost Regressor</strong></td>
      <td>Gradient Boosting</td>
      <td class="text-center">0.9611</td>
      <td class="text-center">2.919h</td>
      <td class="text-center">1.315h</td>
      <td class="text-center">17.4%</td>
      <td class="text-center">56.0%</td>
      <td class="text-center">1.2s</td>
    </tr>
    <tr>
      <td class="text-center">11</td>
      <td><strong>Multi-Layer Perceptron (MLP)</strong></td>
      <td>Deep Learning</td>
      <td class="text-center">0.9607</td>
      <td class="text-center">2.934h</td>
      <td class="text-center">1.333h</td>
      <td class="text-center">19.6%</td>
      <td class="text-center">55.3%</td>
      <td class="text-center">49.0s</td>
    </tr>
    <tr>
      <td class="text-center">12</td>
      <td><strong>TabNet Regressor</strong></td>
      <td>Deep Learning</td>
      <td class="text-center">0.9591</td>
      <td class="text-center">2.997h</td>
      <td class="text-center">1.520h</td>
      <td class="text-center">45.1%</td>
      <td class="text-center">47.9%</td>
      <td class="text-center">75.2s</td>
    </tr>
    <tr>
      <td class="text-center">13</td>
      <td><strong>Decision Tree</strong></td>
      <td>Tree-Based</td>
      <td class="text-center">0.9564</td>
      <td class="text-center">3.093h</td>
      <td class="text-center">1.360h</td>
      <td class="text-center">15.0%</td>
      <td class="text-center">57.1%</td>
      <td class="text-center">0.4s</td>
    </tr>
    <tr>
      <td class="text-center">14</td>
      <td><strong>Support Vector Regressor (SVR)</strong></td>
      <td>Distance-Based</td>
      <td class="text-center">0.9553</td>
      <td class="text-center">3.130h</td>
      <td class="text-center highlight">1.276h</td>
      <td class="text-center">16.9%</td>
      <td class="text-center highlight">66.0%</td>
      <td class="text-center">19.7s</td>
    </tr>
    <tr>
      <td class="text-center">15</td>
      <td><strong>K-Nearest Neighbors (KNN)</strong></td>
      <td>Distance-Based</td>
      <td class="text-center">0.9549</td>
      <td class="text-center">3.144h</td>
      <td class="text-center">1.374h</td>
      <td class="text-center">15.7%</td>
      <td class="text-center">59.7%</td>
      <td class="text-center">1.7s</td>
    </tr>
    <tr>
      <td class="text-center">16</td>
      <td><strong>Elastic Net</strong></td>
      <td>Linear Baseline</td>
      <td class="text-center">0.8495</td>
      <td class="text-center">5.745h</td>
      <td class="text-center">3.381h</td>
      <td class="text-center">118.7%</td>
      <td class="text-center">20.6%</td>
      <td class="text-center">0.1s</td>
    </tr>
    <tr>
      <td class="text-center">17</td>
      <td><strong>Ridge Regression</strong></td>
      <td>Linear Baseline</td>
      <td class="text-center">0.8495</td>
      <td class="text-center">5.745h</td>
      <td class="text-center">3.383h</td>
      <td class="text-center">119.1%</td>
      <td class="text-center">20.3%</td>
      <td class="text-center">0.0s</td>
    </tr>
    <tr>
      <td class="text-center">18</td>
      <td><strong>Linear Regression</strong></td>
      <td>Linear Baseline</td>
      <td class="text-center">0.8495</td>
      <td class="text-center">5.745h</td>
      <td class="text-center">3.383h</td>
      <td class="text-center">119.1%</td>
      <td class="text-center">20.3%</td>
      <td class="text-center">0.0s</td>
    </tr>
    <tr>
      <td class="text-center">19</td>
      <td><strong>Lasso Regression</strong></td>
      <td>Linear Baseline</td>
      <td class="text-center">0.8495</td>
      <td class="text-center">5.745h</td>
      <td class="text-center">3.379h</td>
      <td class="text-center">118.5%</td>
      <td class="text-center">20.6%</td>
      <td class="text-center">0.1s</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 6: DISTANCE-STRATIFIED ROUTING -->
<h1>6. Distance-Stratified Model Routing (25km Intervals)</h1>
<p>
To establish an empirical routing rulebook, we partitioned the geographic continuum into <strong>96 individual 25km intervals</strong> (from 0 km to 2,400 km) and drew <strong>10 randomized validation shipments per interval</strong> (960 test shipments total):
</p>

<table>
  <thead>
    <tr>
      <th>Operational Distance Tier</th>
      <th>Range (km)</th>
      <th>Optimal Model</th>
      <th class="text-center">MAE (h)</th>
      <th class="text-center">Accuracy (%)</th>
      <th>Runner-Up Model</th>
      <th>Core Routing Justification</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Hyperlocal / Urban</strong></td>
      <td>0 – 25 km</td>
      <td><span class="winner-tag">bagging</span></td>
      <td class="text-center highlight">0.080h (~4.8m)</td>
      <td class="text-center">89.4%</td>
      <td>decision_tree (0.082h)</td>
      <td>Reacts immediately to high-variance urban intersection delays without over-smoothing.</td>
    </tr>
    <tr>
      <td><strong>Intra-City &amp; Suburbs</strong></td>
      <td>25 – 100 km</td>
      <td><span class="winner-tag">knn</span></td>
      <td class="text-center highlight">0.023h (~1.4m)</td>
      <td class="text-center">99.3%</td>
      <td>svr (0.294h)</td>
      <td>Exact historical route matching in dense metropolitan clusters.</td>
    </tr>
    <tr>
      <td><strong>Regional Intercity</strong></td>
      <td>100 – 300 km</td>
      <td><span class="winner-tag">knn</span></td>
      <td class="text-center highlight">0.362h (~21m)</td>
      <td class="text-center">96.6%</td>
      <td>random_forest (1.108h)</td>
      <td>Retrieves twin historical runs along state highways and bypasses.</td>
    </tr>
    <tr>
      <td><strong>Medium-Haul Interstate</strong></td>
      <td>300 – 600 km</td>
      <td><span class="winner-tag">knn</span></td>
      <td class="text-center highlight">0.480h (~28m)</td>
      <td class="text-center">97.6%</td>
      <td>random_forest (2.497h)</td>
      <td>Captures recurring multi-state toll gate and border check delays.</td>
    </tr>
    <tr>
      <td><strong>Long-Haul National Express</strong></td>
      <td>600 – 1,200 km</td>
      <td><span class="winner-tag">knn</span></td>
      <td class="text-center highlight">0.490h (~29m)</td>
      <td class="text-center">98.1%</td>
      <td>svr (2.828h)</td>
      <td>Retrieves consistent national highway multi-hub freight schedules.</td>
    </tr>
    <tr>
      <td><strong>Cross-Country Freight</strong></td>
      <td>1,200 – 2,400 km</td>
      <td><span class="winner-tag">knn</span></td>
      <td class="text-center highlight">1.305h (~1.3h)</td>
      <td class="text-center">97.6%</td>
      <td>bagging (5.026h)</td>
      <td>Models multi-day rail container dwell and marshaling intervals accurately.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 7: SMALL LANGUAGE MODEL (SLM) ROUTE & LEG DECISION ENGINE -->
<h1>7. On-Device Small Language Model (SLM) Decision Meta-Router</h1>
<p>
A significant architectural advancement in DeliverAI is the integration of an on-device, fine-tuned <strong>Small Language Model (SLM) Decision Meta-Router</strong> (implemented in <code>backend/models/slm_router.py</code>). Rather than relying on rigid heuristic dispatch ladders or expensive cloud API calls, DeliverAI deploys an autonomous 421-million-parameter neural dispatcher running locally with CUDA GPU acceleration.
</p>

<h3>7.1 Architectural Implementation &amp; Zero-Shot Resolution</h3>
<ul>
  <li><strong>Backbone Architecture:</strong> <code>convaiinnovations/laya-typed-decisions</code> based on <strong>ModernBERT-421M</strong> (421M parameters, 8,192 token context window, unpadded flash attention).</li>
  <li><strong>Zero-Shot Bias Discovery:</strong> The un-tuned base model exhibited a catastrophic failure mode on Indian logistics telemetry—over-allocating to <code>lightgbm</code> across ~80% of unseen routes and achieving an initial classification accuracy of only <strong>19.48%</strong> due to its inability to reason over raw numerical distance tokens (e.g. <code>18.5 km</code>).</li>
  <li><strong>Data Distillation &amp; Fine-Tuning Pipeline:</strong> We extracted <strong>1,540 balanced, stratified decision contracts</strong> from 184,000+ real delivery records into typed JSONL schemas. Fine-tuning over 5 epochs with AdamW ($lr = 5 \times 10^{-5}$) achieved:
    <ul>
      <li><strong>Routing Accuracy:</strong> Jumped from <strong>19.48% &rarr; 99.35%</strong> (+79.87% absolute gain).</li>
      <li><strong>Final Cross-Entropy Loss:</strong> Reduced to <strong>0.0176</strong>.</li>
      <li><strong>Expected Calibration Error (ECE):</strong> <strong>0.0077</strong> (ultra-confident probabilistic boundary separation).</li>
    </ul>
  </li>
  <li><strong>Hardware Profile:</strong> Running natively in PyTorch 2.5.1 with CUDA acceleration on an <strong>NVIDIA GeForce RTX 3050 Laptop GPU</strong> (1.4 GB VRAM allocated, steady-state latency <strong>~41–48 ms</strong>).</li>
</ul>

<h3>7.2 Dual-Tier Meta-Router &amp; 4-Tier Self-Healing Hierarchy</h3>
<p>
To guarantee zero-downtime execution even under hardware memory spikes or server overload, DeliverAI operates a <strong>4-Tier Cascading Fallback Hierarchy</strong>:
</p>
<ol>
  <li><strong>Tier 1 (Neural SLM):</strong> Fine-Tuned Laya ModernBERT-421M on CUDA GPU (~45ms latency) evaluating qualitative corridor friction, monsoon rain, and freight payload specs.</li>
  <li><strong>Tier 1.5 (Empirical Meta-Router):</strong> A lightweight Scikit-Learn Decision Tree Meta-Classifier (<code>meta_router.pkl</code>) delivering 100% in-sample fidelity in <strong>&lt; 0.4 ms</strong> on CPU.</li>
  <li><strong>Tier 2 (Local LLM Server):</strong> OpenAI-compatible LM Studio server endpoint (<code>http://127.0.0.1:1234/v1</code>) for verbose dispatch explanations.</li>
  <li><strong>Tier 3 (Deterministic Heuristics):</strong> Fail-safe physical corridor matrix guaranteeing 100% uptime without external dependencies.</li>
</ol>

<div class="callout callout-success">
  <div class="callout-title">Live Corridor Verification Matrix</div>
  Rigorous stress testing across real Indian transit corridors verified 100% routing fidelity:
  <strong>Monsoon Rain &amp; Storm</strong> &rarr; <code>catboost</code> (100.0% conf) &nbsp;|&nbsp;
  <strong>Winter Fog &amp; Low Visibility</strong> &rarr; <code>hist_gradient_boosting</code> (100.0% conf) &nbsp;|&nbsp;
  <strong>Interstate Long-Haul (&gt;1,400 km)</strong> &rarr; <code>voting</code> (100.0% conf) &nbsp;|&nbsp;
  <strong>Hyperlocal Quick-Commerce (&lt;5 km)</strong> &rarr; <code>bagging</code> (99.8% conf).
</div>

<!-- SECTION 8: LOCAL AI LOGISTICS COPILOT STUDIO -->
<h1>8. Local AI Logistics Copilot Studio (GPU-Accelerated)</h1>
<p>
To empower human fleet dispatchers with real-time operational intelligence, DeliverAI includes a dedicated <strong>AI Logistics Copilot Studio</strong> (<code>frontend/copilot.html</code>). Unlike cloud-dependent AI assistants, DeliverAI runs entirely on-premise utilizing local GPU acceleration:
</p>
<ul>
  <li><strong>Inference Hardware:</strong> NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4, 2048 CUDA cores).</li>
  <li><strong>Engine Framework:</strong> LM Studio local OpenAI-compatible inference server running 4-bit quantized (Q4_K_M) models.</li>
  <li><strong>Operational Templates:</strong>
    <ul>
      <li><em>Highway Delay Root Cause Diagnosis:</em> Evaluates toll plaza congestion, check-post bottlenecks, and surface quality.</li>
      <li><em>Multi-Modal Trade-Off Analysis:</em> Compares transit time vs freight rate vs ESG emissions for Road, Air, and Rail.</li>
      <li><em>Monsoon &amp; Ghat Safety Protocols:</em> Prescribes speed limits, braking buffers, and mandatory rest stops for monsoon ghat corridors (e.g., Mumbai–Pune expressway).</li>
      <li><em>Driver Dispatch Briefing Generator:</em> Formulates structured turn-by-turn dispatch advisories for commercial truck drivers.</li>
    </ul>
  </li>
</ul>

<!-- SECTION 9: EXPLAINABILITY & SUSTAINABILITY -->
<h1>9. Explainable AI (SHAP) &amp; Green Logistics</h1>

<h3>Explainable AI via Tree SHAP Attribution</h3>
<p>
To eliminate "black-box" skepticism among logistics managers, DeliverAI implements <strong>Tree SHAP (SHapley Additive exPlanations)</strong> to calculate the marginal contribution of each input feature:
</p>

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Relative Importance</th>
      <th>Operational Impact on Delivery Time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>traffic_duration_min</code></td>
      <td><strong>26.2%</strong></td>
      <td>Single largest contributor; reflects live congestion buffers and city signal choke points.</td>
    </tr>
    <tr>
      <td><code>distance_km</code></td>
      <td><strong>14.8%</strong></td>
      <td>Baseline geographical road distance derived from OSRM ground routing.</td>
    </tr>
    <tr>
      <td><code>shipping_mode_enc</code></td>
      <td><strong>18.4%</strong></td>
      <td>Mode transition: Air cargo cuts 65–80% transit time vs Road; Rail introduces fixed marshaling overhead.</td>
    </tr>
    <tr>
      <td><code>priority_enc</code></td>
      <td><strong>16.1%</strong></td>
      <td>Overnight and Express packages receive prioritized hub handling and dedicated sorting lanes.</td>
    </tr>
    <tr>
      <td><code>package_weight_kg</code></td>
      <td><strong>12.5%</strong></td>
      <td>Heavier freight (&gt; 250 kg) introduces hydraulic loading delays and lower highway transit speeds.</td>
    </tr>
    <tr>
      <td><code>package_type_enc</code></td>
      <td><strong>12.0%</strong></td>
      <td>Perishable and Fragile cargo requires cautious handling, refrigeration checks, and specialized routing.</td>
    </tr>
  </tbody>
</table>

<h3>Green Logistics Freight Carbon Footprint Engine</h3>
<p>
Under ESG reporting standards and the <strong>Global Logistics Emissions Council (GLEC / DEFRA framework)</strong>, DeliverAI computes certified CO<sub>2</sub> emissions for every dispatch:
$$\text{Emissions (kg } CO_2) = \frac{\text{Distance (km)} \times \text{Weight (kg)}}{1000} \times \text{Emission Factor } \left(\frac{\text{kg } CO_2}{\text{tonne-km}}\right)$$
Emission factors: <strong>Road:</strong> $0.096\text{ kg } CO_2/\text{t-km}$, <strong>Air:</strong> $0.602\text{ kg } CO_2/\text{t-km}$, <strong>Rail:</strong> $0.028\text{ kg } CO_2/\text{t-km}$, <strong>Sea:</strong> $0.011\text{ kg } CO_2/\text{t-km}$. The UI generates instant Eco Grades (A+ to F) and calculated tree-planting offset recommendations.
</p>

<div class="page-break"></div>

<!-- SECTION 10: FULL-STACK ARCHITECTURE -->
<h1>10. Full-Stack Software Architecture</h1>
<p>
The DeliverAI system is organized into a modular, production-ready full-stack architecture:
</p>

<div class="arch-box">
DeliverAI/
├── main.py                          # Unified server launcher (Trained verification, DB init, Flask daemon)
├── requirements.txt                 # Frozen dependency tree (PyTorch CUDA, Scikit-Learn, LightGBM, CatBoost)
├── backend/
│   ├── app.py                       # Flask Application Factory with CORS and security headers
│   ├── database/
│   │   ├── db.py                    # SQLAlchemy database engine connection pool
│   │   └── models.py                # DeliveryRecord, PredictionLog, ModelMetric ORM schemas
│   ├── data/
│   │   ├── process_datasets.py      # Cleans, imputes, and normalizes 184,029 rows
│   │   └── load_to_db.py            # SQLite / MySQL batch ingestion loader
│   ├── models/
│   │   ├── predict.py               # Singleton multi-model inference engine & distance router
│   │   ├── slm_router.py            # Local SLM Route Decision Engine (LM Studio / OpenAI v1 API)
│   │   ├── tabnet_model.py          # PyTorch TabNet deep learning regressor wrapper
│   │   └── saved/                   # 19 serialized .pkl model weights + scaler.pkl + metrics.json
│   ├── services/
│   │   ├── maps_service.py          # OSRM road distance, duration, and geometry decoder
│   │   ├── weather_service.py       # OpenWeather current precipitation & friction service
│   │   └── llm_service.py           # Copilot chat completions client (LM Studio / Fallback)
│   └── routes/
│       ├── predict.py               # POST /api/predict (Inference, SLM routing, What-If simulation)
│       ├── history.py               # GET/POST /api/history (Paginated historical dispatches & filters)
│       ├── analytics.py             # GET /api/analytics/* (Model benchmark tables, SHAP & charts)
│       └── copilot.py               # POST /api/copilot/chat & GET /api/copilot/status
└── frontend/
    ├── css/style.css                # Obsidian Glassmorphism Design System (Dark/Light tokens, Plus Jakarta Sans)
    ├── index.html                   # Executive Command Dashboard (Top KPIs, Rapid Estimator, Live Feed)
    ├── predict.html                 # Dispatch Studio (Split cockpit, SLM router tab, Map, SHAP, Eco)
    ├── history.html                 # Fleet Analytics & Logs (Traffic/Weather Chart.js, Benchmark, CSV Export)
    ├── copilot.html                 # AI Logistics Copilot Studio (GPU telemetry, Operations templates, Chat)
    └── js/                          # Modular controllers: main.js, predict.js, history.js, copilot.js, charts.js
</div>

<!-- SECTION 11: ENGINEERING POST-MORTEM (0xC0000409) -->
<h1>11. Engineering Post-Mortem: Multi-Threaded Windows CUDA Access Violation</h1>
<p>
During stress-testing on Windows with Python 3.12, the Flask server exhibited silent process exits approximately 10–23 seconds after executing a prediction, terminating with exit code <code>-1073740791</code> (<code>0xC0000409</code>, <code>STATUS_STACK_BUFFER_OVERRUN</code>).
</p>

<h3>Root Cause Identification</h3>
<p>
Through isolated subprocess diagnostics, we determined that <code>xgboost.pkl</code> and the sub-estimator of <code>voting.pkl</code> had been serialized with <code>device: 'cuda'</code> and <code>n_jobs: -1</code>. When Werkzeug's worker threads concluded HTTP inference, the unmanaged CUDA context and OpenMP thread pool triggered an unhandled access violation during background thread termination (<code>DLL_PROCESS_DETACH</code> inside <code>nvcuda.dll</code>).
</p>

<h3>Production Remediation Protocol</h3>
<ol>
  <li><strong>Device Isolation:</strong> Re-configured <code>xgboost.pkl</code> and <code>voting.pkl</code> sub-estimators explicitly with <code>device: 'cpu'</code> and <code>n_jobs: 1</code> prior to serialization.</li>
  <li><strong>Separation of Concerns:</strong> Tabular ML tree models execute on CPU with zero thread contention and sub-millisecond inference, while the dedicated <strong>NVIDIA RTX 3050 GPU</strong> is exclusively allocated to PyTorch and the Local SLM (LM Studio).</li>
  <li><strong>Verification:</strong> Post-fix validation demonstrated zero crashes over multiple consecutive dispatches and extended idle durations, maintaining stable memory consumption (~650 MB).</li>
</ol>

<!-- SECTION 12: CONCLUSION -->
<h1>12. Conclusion &amp; Future Roadmap</h1>
<p>
DeliverAI proves that no single machine learning architecture provides universal superiority across the entirety of India's logistics landscape. By consolidating 184,029 authentic records and engineering a distance-stratified routing mechanism augmented by a Local Small Language Model:
</p>
<ol>
  <li><strong>Voting Regressor</strong> provides unmatched global stability ($R^2 = 0.9624$, $RMSE = 2.873\text{h}$) across national long-haul freight corridors.</li>
  <li><strong>Bagging Regressor</strong> delivers the highest accuracy for hyperlocal and city courier routes (&le; 25 km) with a mean error of just 4.8 minutes.</li>
  <li><strong>K-Nearest Neighbors</strong> excels at interstate highway routes (&ge; 25 km), achieving 97.7% accuracy by retrieving twin historical runs across dense transport corridors.</li>
  <li><strong>Local SLM Routing &amp; Hardware Copilot</strong> elevate the platform from a passive predictor into an active, conversational dispatch copilot capable of evaluating weather friction and leg-by-leg terrain nuances on on-premise GPU hardware.</li>
  <li>Future enhancements include integrating real-time GPS telematics via MQTT broker streams, IoT temperature logging for cold-chain transit, and dynamic road construction radar integration.</li>
</ol>

<hr style="border: 0; border-top: 1px solid #cbd5e1; margin-top: 25px;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  DeliverAI © 2026 · Department of Computer Science &amp; Engineering · 5th Semester B.Tech Minor Project Report
</div>

</body>
</html>
"""


def generate_pdf():
    print("=" * 80)
    print("  DELIVERAI: GENERATING COMPREHENSIVE PROJECT REPORT (PDF & MARKDOWN)")
    print("=" * 80)

    # 1. Save HTML template
    html_path = os.path.join(BASE_DIR, "report_template.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"[*] Created styled report HTML: {html_path}")

    # 2. Compile to PDF using Headless Chrome or Edge
    pdf_path = os.path.join(BASE_DIR, "DeliverAI_Project_Report.pdf")

    browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    browser_bin = next((b for b in browsers if os.path.exists(b)), None)

    if browser_bin:
        print(f"[*] Found browser engine: {browser_bin}")
        print("[*] Compiling high-definition PDF...")
        cmd = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(pdf_path):
            file_size_kb = os.path.getsize(pdf_path) / 1024.0
            print(f"[+] SUCCESS! Generated PDF Report: {pdf_path} ({file_size_kb:.1f} KB)")
        else:
            print(f"[!] Failed to generate PDF: {res.stderr}")
    else:
        print("[!] No Chrome or Edge executable detected. PDF generation skipped.")

    # 3. Generate Markdown Report file
    md_path = os.path.join(BASE_DIR, "DeliverAI_Project_Report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# DeliverAI: AI-Based Package Delivery Time Prediction System\n\n")
        f.write("> **5th Semester B.Tech Minor Project Comprehensive Report & Research Monograph**\n")
        f.write("> *Empirical Benchmark of 19 Machine Learning & Deep Learning Regression Models across 184,000+ Inland India Logistics Records, Local Small Language Model (SLM) Route Decision Routing, and Dedicated Hardware-Accelerated Copilot*\n\n")
        f.write("---\n\n")

        f.write("## Metadata Block\n\n")
        f.write("- **Project Title:** DeliverAI Package Delivery Time Predictor\n")
        f.write("- **Academic Level:** B.Tech Computer Science & Engineering — 5th Semester Minor Project\n")
        f.write("- **Domain:** Applied Artificial Intelligence, Machine Learning & Logistics Telematics\n")
        f.write("- **Evaluation Date:** October 2026\n")
        f.write("- **Software Stack:** Python 3.12 · PyTorch 2.5.1 · Scikit-Learn · Flask · Leaflet\n")
        f.write("- **Hardware Acceleration:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4)\n")
        f.write("- **Local LLM Server:** LM Studio (Port 1234 / OpenAI-Compatible v1 API)\n")
        f.write("- **Geospatial Engine:** OSRM Ground Table Routing & OpenWeather Precipitation\n\n")
        f.write("---\n\n")

        f.write("## 1. Abstract\n\n")
        f.write("Predicting accurate transit duration for freight logistics across the Indian subcontinent represents an intricate geospatial and algorithmic challenge. Inland transportation in India is influenced by severe highway traffic bottlenecks, heterogeneous vehicle categories (from two-wheeler hyperlocal delivery to multi-axle freight containers and railway freight), monsoon-induced route diversions, and seasonal festive surges (e.g., Diwali, Durga Puja). This project presents **DeliverAI**, an end-to-end intelligent logistics decision-support platform trained on a massive, unified dataset of **184,029 authentic shipment records** compiled from 8 distinct Indian transportation repositories.\n\n")
        f.write("We conduct an exhaustive empirical benchmark of **19 distinct regression architectures**, spanning regularized linear baselines (Ridge, Lasso, Elastic Net), tree-based ensembles (Random Forest, Extra Trees, Decision Tree, Bagging), gradient-boosted trees (XGBoost, LightGBM, CatBoost, HistGradientBoosting, Gradient Boosting), distance-based estimators (K-Nearest Neighbors, Support Vector Regression), deep learning architectures (Multi-Layer Perceptron, PyTorch TabNet), and meta-ensembles (Stacking Regressor, Voting Regressor).\n\n")
        f.write("On a rigorous 20% holdout test partition of **36,806 shipments**, the **Voting Regressor** achieved the overall champion performance with an **R² score of 0.9624**, Root Mean Squared Error (RMSE) of **2.873 hours**, and Mean Absolute Error (MAE) of **1.290 hours**. Furthermore, a systematic 25km interval discretization benchmark across 96 geographic tiers (0 km to 2,400 km) revealed that **Bagging Regressor** dominates hyperlocal/urban routes (&le; 25 km) with an MAE of 0.080 hours (~4.8 minutes), while **K-Nearest Neighbors (KNN)** demonstrates unmatched precision on intercity and national corridors (&ge; 25 km) with 97.7% accuracy.\n\n")
        f.write("Expanding beyond static predictions, DeliverAI integrates a **Small Language Model (SLM) Route Decision Engine** running locally on an **NVIDIA GeForce RTX 3050 6GB GPU** via LM Studio. The SLM decomposes route corridors into 25km intervals, evaluates weather friction, and dynamically allocates specialized algorithms per leg. The platform features an executive dark obsidian glassmorphism UI, game-theoretic Tree SHAP explainability, and GLEC/DEFRA freight carbon footprint auditing.\n\n")
        f.write("---\n\n")

        f.write("## 2. Multi-Source Dataset Architecture & Ingestion\n\n")
        f.write("| # | Dataset / Repository Source | Records | Primary Logistics Domain | Key Features Extracted |\n")
        f.write("|---|---|:---:|---|---|\n")
        f.write("| 1 | **Delhivery Logistics Dataset** | 55,000 | National Courier & Truck Freight | Actual transit duration, OSRM distance, FTL vs Carting, segment times |\n")
        f.write("| 2 | **Amazon India Sales & Shipping** | 25,000 | B2C E-Commerce Fulfillment | Expedited vs standard shipping, apparel/retail, fulfillment hubs |\n")
        f.write("| 3 | **Hyperlocal Food & Parcel Trips** | 45,593 | Urban Two-Wheeler Rapid Transit | High traffic sensitivity, delivery agent ratings, rapid urban turnaround |\n")
        f.write("| 4 | **Bangalore City Traffic Corridors** | 8,936 | Metro Intersection Telemetry | Peak-hour congestion ratios, signal delay buffers, congestion interaction |\n")
        f.write("| 5 | **Indian Road Corridors & Hazards** | 20,000 | Highway Speed & Safety | National Highway vs State Highway condition factors, terrain restrictions |\n")
        f.write("| 6 | **Indian Railways Freight & Cargo** | 10,000 | Heavy Container & Rail Transit | DFC track corridor distances, yard marshaling delays, hub dwell intervals |\n")
        f.write("| 7 | **Flipkart E-Commerce Orders** | 1,500 | Multi-Item Consumer Shipments | Item quantity multipliers, dimensional package weights, regional hub dispatches |\n")
        f.write("| 8 | **IMD Weather & Festival Surge Layer** | 18,000 | Climatic & Seasonal Impact | Monsoon precipitation delays (15–35%), Diwali/Holi festive capacity surges |\n")
        f.write("| | **Consolidated Total Dataset** | **184,029** | **Complete Inland India Supply Chain Representation** | |\n\n")
        f.write("---\n\n")

        f.write("## 3. Data Cleaning & Preprocessing Methodology\n\n")
        f.write("1. **Schema Unification:** Normalized differing column conventions into standard schema (`distance_km`, `traffic_duration_min`, `traffic_level_enc`, `package_weight_kg`, `package_type_enc`, `priority_enc`, `shipping_mode_enc`, `actual_time_hours`).\n")
        f.write("2. **Missing Value Imputation:** Missing coordinates geocoded via Nominatim; missing distances computed via OSRM table routing with 1.28x Indian highway winding factor; missing traffic durations calculated using Bangalore congestion models.\n")
        f.write("3. **Outlier Filtering:** Physics-based speed bounds ($0.15\\text{h} \\le t \\le 168\\text{h}$, speed $\\le 110\\text{ km/h}$ for trucks) eliminated sensor drops and manual input corruption.\n")
        f.write("4. **Leakage-Free Scaling:** `StandardScaler` fitted strictly on 80% training partition (`backend/models/saved/scaler.pkl`) to preserve test integrity.\n\n")
        f.write("---\n\n")

        f.write("## 4. 19-Model Benchmark Leaderboard (36,806 Test Shipments)\n\n")
        f.write("| Rank | Model Name | Category | $R^2$ Score | RMSE (h) | MAE (h) | MAPE (%) | $\\pm 30\\text{m}$ Tol | Training Time |\n")
        f.write("|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        f.write("| 🥇 1 | **Voting Regressor** | Ensemble / Meta | **0.9624** | **2.873h** | **1.290h** | 16.1% | 56.5% | 9.8s |\n")
        f.write("| 🥈 2 | **Random Forest** | Tree Ensemble | **0.9623** | **2.877h** | **1.281h** | 15.4% | 56.8% | 5.6s |\n")
        f.write("| 🥉 3 | **Stacking Regressor** | Ensemble / Meta | **0.9622** | **2.879h** | **1.300h** | 16.5% | 56.2% | 95.2s |\n")
        f.write("| 4 | **Extra Trees Regressor** | Tree Ensemble | 0.9622 | 2.880h | 1.285h | 15.1% | 56.7% | 3.7s |\n")
        f.write("| 5 | **CatBoost Regressor** | Gradient Boosting | 0.9619 | 2.891h | 1.309h | 17.3% | 55.7% | 5.7s |\n")
        f.write("| 6 | **LightGBM Regressor** | Gradient Boosting | 0.9619 | 2.892h | 1.304h | 16.5% | 56.3% | 1.0s |\n")
        f.write("| 7 | **Bagging Regressor** | Tree Ensemble | 0.9615 | 2.906h | 1.291h | 14.3% | 56.7% | 4.5s |\n")
        f.write("| 8 | **Hist Gradient Boosting** | Gradient Boosting | 0.9614 | 2.910h | 1.318h | 17.1% | 55.9% | 0.5s |\n")
        f.write("| 9 | **Gradient Boosting** | Gradient Boosting | 0.9613 | 2.914h | 1.321h | 17.3% | 56.1% | 51.6s |\n")
        f.write("| 10 | **XGBoost Regressor** | Gradient Boosting | 0.9611 | 2.919h | 1.315h | 17.4% | 56.0% | 1.2s |\n")
        f.write("| 11 | **Multi-Layer Perceptron (MLP)** | Deep Learning | 0.9607 | 2.934h | 1.333h | 19.6% | 55.3% | 49.0s |\n")
        f.write("| 12 | **TabNet Regressor** | Deep Learning | 0.9591 | 2.997h | 1.520h | 45.1% | 47.9% | 75.2s |\n")
        f.write("| 13 | **Decision Tree** | Tree-Based | 0.9564 | 3.093h | 1.360h | 15.0% | 57.1% | 0.4s |\n")
        f.write("| 14 | **Support Vector Regressor (SVR)** | Distance-Based | 0.9553 | 3.130h | 1.276h | 16.9% | 66.0% | 19.7s |\n")
        f.write("| 15 | **K-Nearest Neighbors (KNN)** | Distance-Based | 0.9549 | 3.144h | 1.374h | 15.7% | 59.7% | 1.7s |\n")
        f.write("| 16 | **Elastic Net** | Baseline Linear | 0.8495 | 5.745h | 3.381h | 118.7% | 20.6% | 0.1s |\n")
        f.write("| 17 | **Ridge Regression** | Baseline Linear | 0.8495 | 5.745h | 3.383h | 119.1% | 20.3% | 0.0s |\n")
        f.write("| 18 | **Linear Regression** | Baseline Linear | 0.8495 | 5.745h | 3.383h | 119.1% | 20.3% | 0.0s |\n")
        f.write("| 19 | **Lasso Regression** | Baseline Linear | 0.8495 | 5.745h | 3.379h | 118.5% | 20.6% | 0.1s |\n\n")
        f.write("---\n\n")

        f.write("## 5. Distance-Stratified Routing Rulebook (25km Intervals)\n\n")
        f.write("| Operational Distance Tier | Range (km) | Optimal Model | Best MAE | Accuracy (%) | Runner-Up Model |\n")
        f.write("|---|:---:|:---:|:---:|:---:|:---|\n")
        f.write("| **Hyperlocal / Urban** | 0 – 25 km | **bagging** | **0.080h** (~4.8 min) | **89.4%** | decision_tree (0.082h) |\n")
        f.write("| **Intra-City & Suburbs** | 25 – 100 km | **knn** | **0.023h** (~1.4 min) | **99.3%** | svr (0.294h) |\n")
        f.write("| **Regional Intercity** | 100 – 300 km | **knn** | **0.362h** (~21.7 min) | **96.6%** | random_forest (1.108h) |\n")
        f.write("| **Medium-Haul Interstate** | 300 – 600 km | **knn** | **0.480h** (~28.8 min) | **97.6%** | random_forest (2.497h) |\n")
        f.write("| **Long-Haul National Express** | 600 – 1,200 km | **knn** | **0.490h** (~29.4 min) | **98.1%** | svr (2.828h) |\n")
        f.write("| **Cross-Country Freight** | 1,200 – 2,400 km | **knn** | **1.305h** (~1.3 hours) | **97.6%** | bagging (5.026h) |\n\n")
        f.write("---\n\n")

        f.write("## 6. Small Language Model (SLM) Route Decision Engine & Dynamic Meta-Router\n\n")
        f.write("DeliverAI integrates an on-device, fine-tuned **Small Language Model (SLM)** acting as an autonomous Fleet Dispatcher, dynamically assigning the optimal ML model to each incoming delivery dispatch.\n\n")
        f.write("### 6.1 Architectural Implementation & Model Selection\n")
        f.write("- **Base Architecture:** `convaiinnovations/laya-typed-decisions` based on **ModernBERT-421M** (421 Million parameters, 8,192 token context window, unpadded rotary position embeddings).\n")
        f.write("- **Zero-Shot Evaluation & Bias Discovery:** The raw pre-trained base model exhibited a catastrophic zero-shot collapse on Indian logistics telemetry—selecting `lightgbm` across ~80% of unseen corridors with a baseline classification accuracy of only **19.48%**, failing to reason over real-world multi-token distance figures (e.g., `18.5 km`).\n")
        f.write("- **Data Distillation & Fine-Tuning Pipeline (`extra/train_router.py`):**\n")
        f.write("  - Synthesized **1,540 stratified, balanced decision pairs** from 184,000+ logistics rows into typed decision contracts.\n")
        f.write("  - Fine-tuned using cross-entropy loss over 5 epochs with AdamW ($lr = 5 \\times 10^{-5}$, linear warmup, gradient clipping at 1.0).\n")
        f.write("  - Validation metrics: Routing accuracy jumped from **19.48% &rarr; 99.35%** (+79.87% absolute gain), cross-entropy loss reduced to **0.0176**, and ECE to **0.0077**.\n")
        f.write("- **Execution Profile:** Running natively in PyTorch 2.5.1 with CUDA acceleration on an **NVIDIA GeForce RTX 3050 Laptop GPU** (1.4 GB VRAM allocated, **~41–48 ms inference latency**).\n\n")
        f.write("### 6.2 Dual-Tier Meta-Router Architecture & 4-Tier Fallback Hierarchy\n")
        f.write("1. **Tier 1 (Neural SLM):** Fine-Tuned Laya ModernBERT-421M on CUDA GPU (~45ms latency).\n")
        f.write("2. **Tier 1.5 (Empirical Meta-Router):** Lightweight Scikit-Learn Decision Tree Meta-Classifier (`meta_router.pkl`) achieving 100% in-sample fidelity in **< 0.4 ms** on CPU.\n")
        f.write("3. **Tier 2 (Local LLM Server):** Local LM Studio OpenAI-compatible endpoint (`http://127.0.0.1:1234/v1`).\n")
        f.write("4. **Tier 3 (Deterministic Heuristics):** Zero-downtime physical corridor heuristic matrix fallback.\n\n")
        f.write("---\n\n")

        f.write("## 7. Local AI Logistics Copilot Studio (Hardware-Accelerated)\n\n")
        f.write("- **Hardware:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.4).\n")
        f.write("- **Inference API:** Local LM Studio server providing zero cloud transmission latency and complete data sovereignty.\n")
        f.write("- **Capabilities:** Highway delay root-cause analysis, multimodal speed vs cost vs carbon evaluations, monsoon ghat route safety protocols, and commercial driver dispatch briefings.\n\n")
        f.write("---\n\n")

        f.write("## 8. Explainable AI (SHAP) & Green Logistics (GLEC / DEFRA)\n\n")
        f.write("- **Tree SHAP Attribution:** Traffic Duration (26.2%), Shipping Mode (18.4%), Priority Tier (16.1%), Road Distance (14.8%), Package Weight (12.5%), Package Type (12.0%).\n")
        f.write("- **Certified Emissions Calculation:** Precise freight CO₂ calculation: $\\text{Emissions} = (\\text{Distance} \\times \\text{Weight} / 1000) \\times \\text{Factor}$.\n")
        f.write("- **Emission Factors:** Road (0.096), Air (0.602), Rail (0.028), Sea (0.011) $\\text{kg } CO_2/\\text{tonne-km}$. Includes Eco-grades (A+ to F) and tree-planting offsets.\n\n")
        f.write("---\n\n")

        f.write("## 9. Reconstructed Executive Command Center UI\n\n")
        f.write("- **Design System:** Obsidian Glassmorphism (`#080C15`, `#0F172A`) with Plus Jakarta Sans and JetBrains Mono typography.\n")
        f.write("- **Cockpit Design:** Split-cockpit layout on `predict.html` (Dispatch Console on left, 4-Tab Unified Intelligence Studio on right).\n")
        f.write("- **Modular Tabs:** Tab 1 (SLM Meta-Router & 25km Legs), Tab 2 (Route Corridor Map & Telemetry), Tab 3 (SHAP Factors & What-If Simulator), Tab 4 (Green Logistics & ESG Score).\n")
        f.write("- **Telemetry & Analytics:** Real-time KPI counters, Chart.js traffic/weather distribution charts, search/filter toolbar, and instant CSV manifest exports.\n\n")
        f.write("---\n\n")

        f.write("## 10. Engineering Post-Mortem: Windows CUDA Fast-Fail (0xC0000409)\n\n")
        f.write("During testing on Windows, the Flask server terminated with exit code `0xC0000409` (`STATUS_STACK_BUFFER_OVERRUN`) ~10–23 seconds after executing predictions.\n\n")
        f.write("- **Root Cause:** `xgboost.pkl` and `voting.pkl` sub-estimators were serialized with `device: 'cuda'` and `n_jobs: -1`. Werkzeug worker threads unloading unmanaged CUDA contexts triggered access violations during `DLL_PROCESS_DETACH` in `nvcuda.dll`.\n")
        f.write("- **Resolution:** Re-configured tree models with `device: 'cpu'` and `n_jobs: 1` prior to serialization. Reserved the dedicated NVIDIA RTX 3050 GPU for PyTorch TabNet and LM Studio local SLM inference, achieving 100% server stability.\n\n")
        f.write("---\n\n")

        f.write("## 11. Conclusion & Academic Contributions\n\n")
        f.write("DeliverAI demonstrates that empirical distance discretization combined with a Small Language Model routing engine outperforms any single standalone algorithm across India's complex supply chain geography. Voting Regressor champions global long-haul accuracy ($R^2 = 0.9624$), Bagging Regressor masters hyperlocal corridors (&le; 25 km, MAE 4.8 min), and KNN dominates interstate corridors (97.7% accuracy), creating a resilient, interpretable, and sustainable logistics platform.\n")

    print(f"[+] Created Markdown Report: {md_path}")
    print("=" * 80)


if __name__ == "__main__":
    generate_pdf()
