# Implementation Flow

```
┌───────────────┐   ┌──────────────────┐   ┌───────────────────┐   ┌───────────────┐
│  1. RAW DATA  │→ │ 2. CLEAN/FILTER  │→ │ 3. SMART-CITY      │→ │ 4. DIGITAL TWIN│
│  7 source     │  │ 01_clean_data.py │  │    INDICATORS       │  │  (linked model │
│  files as     │  │ - drop identif.  │  │ - demand, loss,      │  │   across the   │
│  supplied     │  │ - drop constants │  │   growth %           │  │   grid + air   │
│  (01_raw_data)│  │ - fix typos      │  │ - asset age/tier     │  │   layers, keyed│
│               │  │ - reshape wide→  │  │ - AQI trend/season   │  │   on city /    │
│               │  │   tidy           │  │ - RE mix, cost/unit  │  │   taluk)       │
└───────────────┘  └──────────────────┘  └───────────────────┘  └───────┬────────┘
                                                                          │
        ┌─────────────────────────────────────────────────────────────┘
        ▼
┌────────────────────┐   ┌─────────────────────┐   ┌──────────────────────┐
│ 5. ANALYSIS / ML    │→ │ 6. RISK/STRESS       │→ │ 7. WHAT-IF SIMULATION │
│ 02_infra_risk.py    │  │    ASSESSMENT        │  │ (dashboard tab,       │
│ - rule-based        │  │ - substation risk     │  │  client-side JS,      │
│   substation score  │  │   bands (High/Med/   │  │  disclosed formulas)  │
│ 03_aqi_forecast.py  │  │   Low)                │  │ - consumer growth     │
│ - Linear Regression │  │ - taluk risk rollup   │  │ - loss reduction      │
│   (trend+seasonal)  │  │ - AQI holdout metrics │  │ - renewable mix       │
│   on 24-mo AQI      │  │   reported as an      │  │ - substation upgrade  │
│   series             │  │   honest risk flag    │  │   investment          │
└──────────────────────┘  └──────────────────────┘  └──────────┬───────────┘
                                                                  ▼
                                                     ┌────────────────────────┐
                                                     │ 8. DASHBOARD            │
                                                     │ 04_build_dashboard_     │
                                                     │   dataset.py            │
                                                     │  → dashboard_data.json  │
                                                     │  → published HTML       │
                                                     │    artifact (6 tabs:    │
                                                     │    Overview, Infra &    │
                                                     │    Risk, Energy, RE &   │
                                                     │    Cost, Air Quality,   │
                                                     │    What-If)             │
                                                     └────────────────────────┘
```

## Why datasets are linked the way they are
- **City-level BESCOM tables** (Energy Requirement, Consumers, Units Sold,
  Operating Ratio, RE Purchase) all share one key: Bengaluru, FY2015-16 (±1
  year) → they're combined into one **Energy Demand & Sustainability**
  view and jointly feed the What-if simulator's growth/loss/renewable
  sliders.
- **Substations** are the only dataset with a sub-city key (district →
  taluk) → they form the **spatial infrastructure layer**, rolled up to
  taluk level for the risk map.
- **Air Quality** is the only time-series-rich dataset → it stands as its
  own **Environmental layer**, linked to the grid layer only at the
  city-wide level (both describe "Bengaluru" as a whole); no dataset
  supplied lets us causally connect grid load to air pollution (e.g. no
  power-plant emissions data), so the twin does not claim that link.
- The **What-if tab** is the integration point: every slider pulls its
  *baseline* value from a real cleaned number (7.42% consumer growth,
  12.03% distribution loss, ₹4.15/unit RE cost, etc.) — nothing is a magic
  number.

## Tech used
- **Cleaning/derivation:** Python (pandas) — `05_analysis_ml/*.py`
- **Risk scoring:** rule-based (documented weights), not ML — see
  `02_RISK_METHODOLOGY.md`
- **Forecasting:** scikit-learn `LinearRegression` — see
  `03_AQI_FORECAST_MODEL.md`
- **Dashboard:** single self-contained HTML file, Chart.js (via CDN) +
  hand-built SVG schematic map, published as a Claude Artifact and also
  saved as a standalone file
