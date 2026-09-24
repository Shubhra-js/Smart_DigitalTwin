# Bengaluru Smart-City Digital Twin — Project Documentation

## What this project is
A working digital twin of Bengaluru's **electricity grid + air quality** built
entirely from the 7 datasets supplied (6 BESCOM operational tables + 1 CPCB
air-quality series). It follows the pipeline:

```
Raw Data → Cleaning → Smart-City Indicators → Digital Twin →
Analysis/ML → Risk/Stress Assessment → What-if Simulation → Dashboard
```

Every stage is a real file in this folder, not a slide — you can open the
scripts, the cleaned CSVs, and the dashboard and trace every number back to
its source row.

## Folder guide

| Folder | Contents |
|---|---|
| `01_raw_data/` | Untouched copies of the 8 files you provided |
| `02_cleaned_data/` | 7 tidy, analysis-ready CSVs (one per dataset) |
| `03_curated_reference_data/` | The **only** non-source data in this project: approximate taluk map centroids (needed to plot a map — no coordinates existed in your data) and the published CPCB India AQI category bands (public national standard, used only as a reference overlay). Both are clearly labelled and never presented as measured data. |
| `04_documentation/` | This file + per-dataset decision log, pipeline architecture, scenario design, limitations |
| `05_analysis_ml/` | The 4 Python scripts that do all cleaning/scoring/forecasting, plus their output CSVs in `outputs/` |
| `06_dashboard/` | `dashboard_data.json` (consolidated data feeding the dashboard) + the dashboard source. **The live dashboard is published as a Claude Artifact** (see chat) — it is also saved as a standalone HTML file you can open in any browser. |

## Why the project is scoped the way it is
All 7 source datasets are BESCOM (electricity utility) operational tables
plus one air-quality series — there is no water, traffic, waste, or
population dataset in what you supplied. So the twin is honestly a
**grid + air infrastructure twin**, not a full city twin. Section
"Extending the Twin" in `PIPELINE.md` lists exactly what additional datasets
would be needed to extend it to water, mobility or waste layers, so the
architecture is ready to absorb them without redesign.

## How to regenerate everything
```
cd 05_analysis_ml
python3 01_clean_data.py                # raw -> 02_cleaned_data/
python3 02_infrastructure_risk_score.py # rule-based risk index -> outputs/
python3 03_aqi_forecast_model.py        # linear-regression AQI forecast -> outputs/
python3 04_build_dashboard_dataset.py   # consolidates everything -> 06_dashboard/dashboard_data.json
```
Then re-embed `dashboard_data.json` into `06_dashboard/template.html` (see
the one-line Python snippet in `PIPELINE.md`) to rebuild the dashboard HTML.
