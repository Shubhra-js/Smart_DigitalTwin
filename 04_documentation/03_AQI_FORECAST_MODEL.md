# Air Quality Forecast — Model Card

## Why ML is justified here (and nowhere else in this project)
This is the only dataset with a real, evenly-spaced time series: 24
consecutive monthly PM2.5/PM10 readings. That's enough points to fit and
**honestly validate** a simple model — every other dataset in this project
has 1–3 time points, which is why ML was deliberately not used there.

## Model
- **Algorithm:** Linear Regression (one per pollutant — PM2.5 and PM10).
- **Input features:**
  - `month_index` — 1..24, captures the long-run trend
  - `sin(2π·month/12)`, `cos(2π·month/12)` — captures the annual seasonal
    cycle that is visible in the actual data (higher PM in Nov–Feb "winter
    smog", lower in Jun–Sep monsoon months)
- **Target:** monthly mean PM2.5 (µg/m³) / PM10 (µg/m³)
- **Output:** fitted historical line + 6-month-ahead forecast (Jan–Jun 2019)
- **Why so simple:** with only 24 samples, a more complex model (random
  forest, polynomial, ARIMA with many parameters) would overfit noise and
  give a false sense of precision. 3 features / linear model is the
  complexity ceiling this data size can honestly support.

## Validation (holdout, last 4 months withheld from training)
| Pollutant | Holdout MAE | Holdout R² | Training samples |
|---|---|---|---|
| PM2.5 | ~20.6 µg/m³ | **-9.2 (negative)** | 20 |
| PM10  | ~12.2 µg/m³ | **-2.5 (negative)** | 20 |

**A negative R² means the model performs worse than simply predicting the
recent average** for those 4 held-out months. This is disclosed prominently
in the dashboard's Air Quality tab (not hidden) — the forecast should be
read as an *illustrative trend direction only*, useful for showing how a
what-if model *would* work once more months of data are available, not as
an operational forecast BESCOM/BBMP should plan against.

## Honest takeaway for the project
This model demonstrates the **mechanism** (trend + seasonality → forecast)
that a real air-quality early-warning system would use, but flags — by its
own reported metrics — that 24 monthly points are not enough to trust the
output numerically. The recommended next step (see `05_NEXT_DATA_NEEDED.md`)
is daily or weekly granularity data, which would give 10–20× more training
points for the same calendar span.
