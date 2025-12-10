# **System Architecture**

## **Overview**

This project is a full geospatial analytics pipeline and interactive dashboard designed to analyse Chicago crime patterns, detect spatial hotspots, model statistical risk, and forecast future crime levels.
The architecture is composed of four major subsystems:

1. **Data Ingestion & Normalisation**
2. **Spatial Feature Engineering**
3. **Modelling & Forecasting**
4. **Interactive Dash Application**

Each subsystem is modular and can be extended or replaced without disrupting the broader system.

---

## **1. Directory Structure**

```
project/
│
├── data/
│   ├── raw/           # Input datasets (crimes, streetlights, bus stops, boundary)
│   ├── processed/     # Pipeline outputs (grid, model results, reports)
│   └── reports/       # Generated PDF summaries
│
├── src/
│   ├── aggregate.py            # Feature aggregation and temporal feature engineering
│   ├── build_grid.py           # Hexagon grid construction
│   ├── config.py               # Central configuration paths & constants
│   ├── load_data.py            # Data ingestion functions
│   ├── model_poisson_nb.py     # GLM models (Poisson & Negative Binomial)
│   ├── model_rf_gwr.py         # ML and spatial models (Random Forest, GWR)
│   ├── reporting.py            # PDF summary report generation
│   ├── spatial_stats.py        # Spatial autocorrelation, Gi*, KDE
│   ├── timeseries.py           # Monthly forecasting module
│   └── __init__.py
│
├── app/
│   ├── layout.py               # UI layout & components for the Dash app
│   ├── callbacks.py            # Application interactivity & rendering logic
│   ├── maps.py                 # Plotly map rendering: static & animated
│   ├── app.py                  # Dash application
│   └── __init__.py
│
├── run_pipeline.py             # End-to-end pipeline orchestrator
├── run_app.py                  # Entry point for the dashboard
├── requirements.txt
└── README.md
```

---

## **2. Data Flow Pipeline**

### **Step 1: Load Raw Data (`load_data.py`)**

Loads and standardises:

* Crime incidents (`crimes.csv`)
* Streetlight locations
* Bus stop locations
* Chicago city boundary (shapefile)

All geometries are reprojected to a common projected CRS for accurate spatial computation.

**Output:** Cleaned GeoDataFrames.

---

### **Step 2: Build Hexagonal Grid (`build_grid.py`)**

* Generates a uniform hexagonal mesh across the city boundary.
* Hex diameter is configurable (default: **100 metres** for fine-grained analysis).
* Assigns `cell_id` to each hex.

**Output:** `hex_grid.gpkg`

---

### **Step 3: Spatial Aggregation (`aggregate.py`)**

For each hex cell:

* Counts crimes (total and per selected type)
* Counts streetlights and bus stops
* Computes hourly, daily, and monthly temporal summaries
* Constructs enriched per-cell feature vectors

Also assigns each crime event a hexagon ID for temporal modelling.

**Output:**

* `features.parquet` — cell-level feature matrix
* `monthly_cell_crime.parquet` — temporal crime cube

---

## **3. Modelling Architecture**

### **3.1 Classical Statistical Models (`model_poisson_nb.py`)**

* **Poisson Regression:** Baseline count model
* **Negative Binomial Regression:** Handles overdispersion
* Computes:

  * Predicted crime counts
  * Dispersion metrics
  * Goodness-of-fit scores

---

### **3.2 Machine Learning & Spatial Models (`model_rf_gwr.py`)**

* **Random Forest Regressor**

  * Captures nonlinear relationships
  * Feature importances included

* **Geographically Weighted Regression (GWR)**

  * Produces spatially varying coefficients
  * Generates local parameter surfaces for interpretability

Outputs include:

* `pred_rf`
* `pred_gwr`
* GWR coefficient layers

---

## **4. Spatial Statistics (`spatial_stats.py`)**

### **Moran’s I**

* Measures global spatial autocorrelation of crime intensity.

### **Getis-Ord Gi***

* Hotspot detection.
* Produces:

  * **`gi_star`** — local Gi statistic
  * **`gi_z`** — standardized z-scores
  * **`gi_p`** — significance values

### **Kernel Density Estimation (KDE)**

* Computes smoothed crime intensity surfaces.

---

## **5. Time-Series Forecasting (`timeseries.py`)**

* Aggregates historical monthly crime data.
* Fits a lightweight exponential smoothing model.
* Provides:

  * Baseline prediction for 6 upcoming months
  * Confidence ranges
  * Exported forecast table

---

## **6. Dash Application Architecture**

### **UI Layer (`layout.py`)**

Provides:

* Model selector (Observed, Poisson, NB, RF, GWR)
* Crime type selector
* Hour-of-day and day-of-week filters
* Hotspot/Gi* view
* KDE view
* Animation toggles
* CSV & PDF export buttons

Layout is Bootstrap-based with a sidebar + dynamic main panel.

---

### **Callback Layer (`callbacks.py`)**

Handles:

* Tab switching
* Dynamic map rendering (static / animated)
* Statistics tab generation
* Forecast loading & rendering
* PDF and CSV downloads
* Hotspot & KDE graphs

All callbacks are fail-safe and degrade gracefully if data is missing.

---

### **Mapping Layer (`maps.py`)**

* Generates **choropleth mapbox** views
* Includes animated month-by-month crime progression
* Supports multiple colour scales and filters
* Designed for high performance even with thousands of hexagons

---

## **7. Output Artifacts**

### **Produced Automatically:**

| File                         | Description                         |
| ---------------------------- | ----------------------------------- |
| `hex_grid.gpkg`              | Hexagonal grid for spatial indexing |
| `features.parquet`           | Cell-level aggregated features      |
| `monthly_cell_crime.parquet` | Time-indexed crime cube             |
| `model_results.parquet`      | All model predictions & stats       |
| `forecast_monthly.parquet`   | Future crime predictions            |
| `crime_summary_*.pdf`        | Auto-generated analysis reports     |

---

## **8. Technology Stack**

### **Core Libraries**

* Python 3.11+
* GeoPandas / Shapely / PyProj
* libpysal / esda (spatial statistics)
* scikit-learn (machine learning)
* mgwr (geographically weighted regression)
* plotly / dash (visualisation & dashboard)
* statsmodels (classical modelling)
* reportlab (PDF generation)

### **GIS Considerations**

* All spatial computations operate in projected CRS (EPSG:3857 or equivalent)
* Dash maps served in WGS84 (EPSG:4326) for compatibility with Mapbox

---

## **9. Scalability & Optimisation Notes**

* Grid size is configurable for performance tuning
* Vectorised operations used for aggregation
* Numba-dependent processes replaced where possible for stability
* Avoids large in-memory copies of geometries
* Modular pipeline permits parallel execution if required

---

## **10. Future Extensions**

* Deep learning spatial models (e.g., graph neural networks)
* Real-time event ingestion (Kafka / PubSub)
* Spatial join caching for repeated analysis
* Anomaly detection and early-warning indicators