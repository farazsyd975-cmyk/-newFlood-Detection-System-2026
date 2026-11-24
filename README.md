# PUNJAB FLOOD INTELLIGENCE & CAUSE-AWARE RESPONSE PLATFORM
### Advanced AI/ML Flood Hazard Prediction, Diagnostic Causal Inference & Disaster Planning System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)
![Scikit-Learn](https://img.shields.io/badge/ML-Dual%20Random%20Forest%20Ensemble-orange.svg)
![Leaflet](https://img.shields.io/badge/Maps-Leaflet.js%20%7C%20OSM-brightgreen.svg)
![Chart.js](https://img.shields.io/badge/Visualizations-Chart.js%204.4-cyan.svg)
![Database](https://img.shields.io/badge/Database-SQLite%203-blueviolet.svg)
![Deploy](https://img.shields.io/badge/Deploy-Render%20Native-46e3b7.svg)

---

## 1. Executive Platform Overview

The **Punjab Flood Intelligence Platform** is a professional-grade, multi-dimensional disaster management and hydrologic prediction system engineered to monitor, evaluate, and formulate emergency response directives across the vulnerable river basins of **Punjab, India**.

Coupling multivariate atmospheric observations with basin hydrology, the platform predicts **multi-class flood hazard severity** alongside **cause-aware diagnostic classification** and **automated emergency response prioritization** for seven prioritized Punjab districts:
1. **Jalandhar** (Doaba central plain / Kali Bein tributary backwaters)
2. **Phagwara** (East Bein industrial & agricultural drainage depression)
3. **Amritsar** (Ravi River border corridor & Sakki Nullah basin)
4. **Ludhiana** (Dense urban industrial corridor & Buddha Nullah channel)
5. **Kapurthala** (Beas River & Harike Wetland confluence / Mand lowlands)
6. **Hoshiarpur** (Sub-mountainous Shivalik foothill flash torrents / *choes*)
7. **Nawanshahr (SBS Nagar)** (Sutlej River floodplain below Ropar Barrage)

---

## 2. Core Technological Architecture

The platform is built on open-source scientific Python and modern web engineering:
- **Backend Framework**: Python Flask 3.1 with modular blueprint-ready routing and robust JSON REST APIs.
- **Machine Learning Core**: Scikit-Learn dual-engine ensemble (`RandomForestClassifier` with `StandardScaler`):
  - Primary Risk Classifier (130 de-correlated bagged trees, 4 risk tiers: Low, Moderate, High, Severe).
  - Secondary Cause-Aware Diagnostic Classifier (100 bagged trees, 5 causal categories).
- **Cartographic Interface**: Interactive Leaflet.js with custom pulsing risk halos, OpenStreetMap tiles, and critical Punjab flood hotspot overlays (Harike Pattan, Buddha Nullah, Shivalik Choes, Sutlej Dhussi Bunds).
- **Atmospheric Telemetry**: Open-Meteo REST API integrating live temperature, relative humidity, 24h precipitation, and 3-day daily forecasts, backed by automatic fail-safe fallback to regional historical baselines.
- **Embedded Persistence**: SQLite 3 database (`database/flood.db`) with automatic schema initialization, prediction audit logging, early warning alert tracking, and email authentication.
- **Analytics & XAI**: Chart.js 4.4 powering 6 interactive dashboards, 24h hourly precipitation distributions, model confusion matrices, and Gini feature attribution.

---

## 3. The 14 Major Upgrades & Platform Modules

### 1. Advanced Multivariate Flood Prediction
Evaluates 9 domain-grounded hydrological features:
- `rainfall_mm`: 24-hour cumulative rainfall.
- `temp_c`: Ambient surface temperature (°C).
- `humidity_pct`: Relative atmospheric humidity (%).
- `river_water_level_m`: Water gauge level of nearest river relative to local zero datum (m).
- `soil_moisture_pct`: Volumetric moisture saturation of upper soil column (%).
- `prev_rainfall_7d_mm`: 7-day antecedent rainfall representing ground pre-saturation.
- `elevation_m`: Elevation above Mean Sea Level (MSL) in meters.
- `distance_to_river_km`: Proximity from city center to primary natural drainage channel (km).
- `drainage_capacity_pct`: Effective storm channel discharge efficiency (%).

Inference outputs a **continuous composite risk index (0–100%)**, full class probability distributions (Low, Moderate, High, Severe), and calibrated risk classifications.

### 2. Cause-Aware Diagnostic Classification
Identifies the primary causal driver of flooding:
- **Rainfall-Driven Flooding**: Cloudburst or torrential precipitation overpowering surface absorption while rivers remain within banks.
- **Drainage-Driven Flooding**: Moderate-to-heavy precipitation trapped due to choked stormwater channels (e.g. Buddha Nullah), culvert blockages, or low gradient.
- **River Overflow**: River gauge approaching or exceeding danger stage primarily due to upstream dam releases (Bhakra/Pong) rather than local downpours.
- **Combined Flood Risk**: Catastrophic compound convergence of extreme precipitation, saturated soil, choked drainage, and swollen river stage simultaneously (analogous to the July 2023 disaster).
- **Normal Drainage**: Baseline hydrological balance within natural absorption capacity.

Every cause prediction is explicitly presented as a **predicted probable cause** supported by an automated telemetry evidence checklist and non-confirmation disclaimers.

### 3. Interactive Flood Risk Map
- Leaflet.js Punjab map centered at `[31.25°N, 75.50°E]`.
- Dynamic color-coded buffer rings indicating district alert radii.
- Interactive station pins with risk-level pulse animations.
- Punjab flood hotspots toggle (Harike Pattan confluence, Buddha Nullah outfalls, Shivalik torrents, Sutlej dykes).
- **Multi-Station Comparison Tool**: Side-by-side comparative matrix of all 7 stations with interactive Chart.js cross-basin risk scoring.

### 4. Live Weather & Forecast Integration
- Direct Open-Meteo REST API telemetry ingestion.
- 24-Hour hourly rainfall trend chart rendered via Chart.js on the main dashboard.
- 3-Day daily forecast cards (Today, Tomorrow, Day 3) with min/max temperatures, precipitation accumulation, and WMO weather condition descriptions.
- Explicit data source tagging: `🟢 Live Open-Meteo Telemetry` vs `🟡 Regional Baseline (Offline Mode)`.

### 5. Advanced Analytics Dashboard (`/analytics`)
- Monitored basins overview metrics: Active stations, High-risk count, Severe-risk count, Average rainfall.
- Chart 1: Punjab Flood Risk Distribution (Doughnut).
- Chart 2: Location-wise Risk Comparison (Bar chart with risk tiers).
- Chart 3: 24h Rainfall vs River Gauge Stage (Dual-axis chart).
- Chart 4: Historical Monsoon Rainfall & Flood Events (2018–2024).
- Chart 5: Punjab Monthly Monsoon Inflow Trends (May–Oct).
- Chart 6: Basin Drainage Efficiency vs Vulnerability Index.
- Comprehensive district telemetry table with links to individual response plans.

### 6. Explainable AI (XAI) & Sensitivity Analysis
- Transparent feature attribution computed from Random Forest Gini feature importances.
- Primary risk elevating factors and protective mitigating factors with parameter benchmarks.
- **Interactive What-If Sensitivity Explorer**: Instant simulation buttons (`+25mm Downpour`, `+50mm Cloudburst`, `Choke Drainage (-30%)`, `Clear Drainage (+30%)`, `River Surge (+1.0m)`) backed by `/api/sensitivity-analysis` computing real-time risk index shifts.

### 7. Early Warning & Alert Center (`/alerts`)
- Automatic alert generation for High and Severe risk thresholds.
- **Risk Escalation Detection**: Compares current assessment against previous database entries to flag conditions upgraded from Moderate to High or High to Severe (`⚡ RISK ESCALATED`).
- Global alert badge in navigation header and emergency alert strip on the dashboard.
- Individual and bulk alert acknowledgement tools.

### 8. Cause-Aware Emergency Response & Resource Planning (`/response-planning`)
- Operational contingency protocols tailored to severity and cause:
  - Emergency response priority (Priority 1 Critical Emergency, Priority 2 High Alert, Priority 3 Active Monitoring, Priority 4 Routine).
  - Vulnerable sectors requiring immediate monitoring (specific river reaches, canals, low-lying wards).
  - Evacuation protocols (Mandatory Evacuation Orders vs Precautionary Standby vs Normal).
  - Drainage & hydraulic control actions (mechanical diesel de-watering, flap gate operations, dyke patrols).
  - Standardized emergency resource allocation (NDRF/SDRF boat battalions, 100+ HP de-watering pumps, geotextile sandbag reserves, designated community shelters, mobile medical units).
  - Action checklist for District Magistrates and DDMA authorities.

### 9. Historical Data & Provenance (`/history`)
- Historical Punjab monsoon records (2018–2024 annual rainfall and flood event counts).
- Monthly rainfall patterns (May to October averages).
- Persistent SQLite audit log with search, city filter, and risk tier filter.
- Strict provenance labels separating authentic historical records from synthetic benchmarks and live telemetry.

### 10. Model Performance & Architecture Evaluation (`/model`)
- Algorithm explanation: Bagging ensemble with StandardScaler normalization.
- Actual held-out test set metrics (from `model/model_metadata.json`):
  - **Risk Test Accuracy**: **94.05%** (Baseline Decision Tree: 92.14%)
  - **5-Fold Cross-Validation Accuracy**: **91.73% (±1.07%)**
  - **Cause Diagnostic Accuracy**: **96.90%**
  - **Weighted F1-Score**: **93.99%**
  - **Macro F1-Score**: **91.23%**
- Actual 4×4 Confusion Matrix for Low, Moderate, High, Severe risk tiers.
- Interactive Chart.js Feature Importance Chart.
- Class-level classification reports.

### 11. Command-Center User Interface
- Authoritative dark blue, deep navy, and cyan color palette (`#0b132b`, `#1c2541`, `#00b4d8`, `#f8fafc`).
- Professional typography using Inter and Roboto Mono.
- Responsive, high-contrast disaster-management layout with smooth transitions.

### 12. Dataset Ingestion & Export Portal (`/data`)
- Custom CSV dataset upload with drag-and-drop file interface.
- Automatic schema validation and missing-value imputation.
- Batch prediction execution on uploaded data.
- Full prediction audit log export to CSV (`/api/export/predictions-csv`).
- Location-specific JSON intelligence report download (`/api/export/station-report/<name>`).

### 13. Technical Documentation (`/docs`)
- Problem statement, solution architecture, USDA SCS runoff physics formulas, data flow pipelines, algorithmic formulations, limitations, and future research scope.

---

## 4. User Authentication & Default Credentials

| Email Address | Default Password | Role |
|---|---|---|
| `user@floodsystem.com` | `password123` | Default Operator Account |

*(Users can also register new accounts with their own email address via `/register`)*

---

## 5. Local Setup & Execution Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13.

### Step 1: Clone or Navigate to Directory
```bash
cd Flood-Detection-System
```

### Step 2: Set Up Virtual Environment (Recommended)
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Complete Automated Test Suite
Verify all 18 unit, integration, ML, and API test cases:
```bash
python -m unittest tests/test_system.py
```
Expected output:
```
Ran 18 tests in 8.892s
OK
```

### Step 5: (Optional) Retrain Machine Learning Pipelines
To re-synthesize calibrated benchmark data and re-evaluate models:
```bash
python train_model.py
```

### Step 6: Launch the Web Platform
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000`.

---

## 6. Render Cloud Deployment

The repository includes `render.yaml` and `Procfile` configured for deployment on Render.

1. Push your repository to GitHub.
2. Link the repository in [Render](https://render.com) as a **Web Service**.
3. Render automatically executes:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. The service will deploy with full SSL encryption and production-ready WSGI workers.

---

## 7. Scientific Attribution & Provenance
- Hydrological Runoff Physics: Adapted from USDA SCS Curve Number (CN) Method and Central Water Commission (CWC) stage-discharge relations.
- Atmospheric Observations: Open-Meteo Free Weather API.
- Mapping Cartography: © OpenStreetMap contributors via Leaflet.js.
- Historical Benchmarks: IMD Punjab Monsoon Annual Reports (2018–2024).

## 5. Project Directory Structure

```
Flood-Detection-System/
│
├── app.py                      # Flask main server, authentication & API routes
├── train_model.py              # ML training script, evaluation & pipeline persistence
├── requirements.txt            # Python dependencies (pinned versions)
├── Procfile                    # Render/Gunicorn startup command
├── render.yaml                 # Infrastructure as Code configuration for Render
├── README.md                   # Full documentation & setup guide
├── .gitignore                  # Clean repository exclusions
│
├── model/
│   ├── flood_model.pkl         # Trained Random Forest Scikit-Learn pipeline
│   └── model_metadata.json     # Comprehensive evaluation metrics & feature importances
│
├── dataset/
│   ├── flood_data.csv          # Hydrologically calibrated dataset (1,799 rows)
│   └── dataset_metadata.md     # Feature data dictionary & physical formulas
│
├── templates/
│   ├── base.html               # Master layout with navbar & user badge
│   ├── index.html              # Main Punjab interactive map & risk predictor
│   ├── model_info.html         # Model metrics, confusion matrix & technical FAQ
│   ├── history.html            # SQLite historical audit log table
│   ├── login.html              # User email login page
│   └── register.html           # New user registration page
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean university-grade design (navy/white theme)
│   ├── js/
│   │   ├── map.js              # Leaflet.js map, dynamic pin pulse markers & popups
│   │   └── main.js             # Telemetry fetching, slider bindings & prediction controller
│   └── images/
│
├── database/
│   ├── db.py                   # SQLite connection helpers, query routines & auth
│   └── flood.db                # SQLite embedded database file (auto-initialized)
│
├── utils/
│   ├── data_processing.py      # Location definitions, input validation & schemas
│   ├── weather_service.py      # Open-Meteo live observation service with baseline fallback
│   └── prediction.py           # Pipeline loading & real-time probabilistic inference
│
└── tests/
    └── test_system.py          # Automated test suite (13 unit & integration tests)
```

---

## 6. Local Setup & Execution Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Internet connection (optional; required only for initial package install and live Open-Meteo queries).

### Step 1: Clone or Extract the Project
Navigate to the project root directory:
```bash
cd Flood-Detection-System
```

### Step 2: Create and Activate a Virtual Environment
**On Windows (PowerShell / Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Automated Test Suite
Verify all 13 unit, integration, and authentication tests:
```bash
python tests/test_system.py
```
Expected output:
```
Ran 13 tests in 9.363s
OK
```

### Step 5: Start the Flask Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
To log in, click **Login** in the top navigation bar or go to:
```
http://127.0.0.1:5000/login
```

---

## 7. Deployment on Render

This application is configured for deployment on **Render** using Gunicorn.

### Deployment Steps:
1. Push the `Flood-Detection-System` repository to GitHub or GitLab.
2. Log in to [Render](https://render.com) and click **New +** ➔ **Web Service**.
3. Select your repository.
4. Configure the service settings:
   - **Name**: `punjab-flood-detection-system`
   - **Region**: Singapore or Frankfurt (choose nearest)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **Create Web Service**. Render will automatically install dependencies, initialize the database, and assign a live public HTTPS URL.

---

## 8. Academic Credits & License
- Developed as a B.Tech AI/ML Engineering Project.
- Mapping Data: © OpenStreetMap contributors.
- Telemetry: Open-Meteo & Central Water Commission / IMD Historical monsoon baselines.
