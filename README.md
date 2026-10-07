# Bengaluru Smart-City Digital Twin

This repository builds a simple digital twin for Bengaluru using the provided utility and air-quality datasets. It connects:

- electricity demand and infrastructure indicators
- substation risk and performance signals
- air-quality trend forecasting
- a dashboard to explore the combined view

The project is intentionally practical and transparent: it uses cleaned source data, documented rules for risk scoring, and a lightweight forecasting model rather than claiming more than the data supports.

## What is included

- Raw source files in `01_raw_data/`
- Cleaned analysis-ready datasets in `02_cleaned_data/`
- Curated reference data in `03_curated_reference_data/`
- Methodology and project notes in `04_documentation/`
- Python analysis scripts in `05_analysis_ml/`
- Dashboard files in `06_dashboard/`

## Main workflow

1. Raw data is cleaned and standardized
2. Key indicators are derived for grid performance and air quality
3. Infrastructure risk is scored from the cleaned tables
4. AQI is forecast using a simple regression model
5. Results are consolidated into a dashboard dataset
6. The dashboard is opened in the browser for exploration

## Folder overview

### `01_raw_data/`
Original files supplied for the project.

### `02_cleaned_data/`
Tidy CSVs used for analysis and modeling.

### `03_curated_reference_data/`
Reference layers such as AQI category thresholds and taluk centroid data.

### `04_documentation/`
Project documentation, method notes, and limitations.

### `05_analysis_ml/`
Python scripts to run the pipeline.

Key scripts:

- `01_clean_data.py` — cleans the source data
- `02_infrastructure_risk_score.py` — computes risk indicators
- `03_aqi_forecast_model.py` — forecasts AQI for the next months
- `04_build_dashboard_dataset.py` — prepares data for the dashboard

Outputs are stored in `05_analysis_ml/outputs/`.

### `06_dashboard/`
Dashboard assets and output data.

Files include:

- `dashboard_data.json`
- `bengaluru_digital_twin_dashboard.html`
- `template.html`

## Quick start

From the project root, run:

```bash
cd 05_analysis_ml
python 01_clean_data.py
python 02_infrastructure_risk_score.py
python 03_aqi_forecast_model.py
python 04_build_dashboard_dataset.py
```

Then open the dashboard HTML file in a browser:

```bash
cd ..
start 06_dashboard\bengaluru_digital_twin_dashboard.html
```

If needed, use `python3` instead of `python` depending on your environment.

## Scope and limitations

This project is a utility + environmental digital twin for Bengaluru, not a complete city-wide model. The available datasets focus on:

- electricity demand and operational metrics
- substation and infrastructure condition
- air-quality measurements and forecasting

It does not claim causal links beyond what the source data supports.

## Documentation

For deeper detail, see the files in `04_documentation/`, especially:

- `01_DATASET_DECISIONS.md`
- `02_RISK_METHODOLOGY.md`
- `03_AQI_FORECAST_MODEL.md`
- `06_PIPELINE_ARCHITECTURE.md`

## Summary

This repository is a compact, transparent prototype for exploring Bengaluru’s infrastructure and air-quality signals through a data-driven dashboard and simple analytical models.
