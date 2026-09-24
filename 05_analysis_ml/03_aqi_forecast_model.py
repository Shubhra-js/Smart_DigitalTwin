"""
Stage: Analysis/ML -> Prediction (Air Quality layer)
Why ML IS justified here (unlike the BESCOM tables): this is the only
dataset with a genuine time series (24 consecutive monthly points), enough
to fit and sanity-check a simple trend+seasonal model.

Model: Linear Regression
Features (X): month_index (captures long-term trend), sin(2*pi*month/12),
              cos(2*pi*month/12)  (captures the annual seasonal cycle -
              Bengaluru PM2.5/PM10 are known from the data itself to dip in
              monsoon months Jun-Sep and rise in winter Nov-Feb)
Target (y): pm25 (ug/m3), pm10 (ug/m3) - two separate models
Output: forecast for the next 6 months + the fitted historical line, so the
        dashboard can show "actual vs model fit vs forecast" transparently.
Kept deliberately simple (linear regression, 3 features, 24 samples) instead
of a complex model: with only 24 data points a complex model would overfit
and give a false sense of precision. This is disclosed in the dashboard.
"""
import pandas as pd, numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import json

df = pd.read_csv("/home/claude/twin/02_cleaned_data/air_quality_cleaned.csv", parse_dates=["date"])

def make_features(month_index, month_num):
    return np.column_stack([
        month_index,
        np.sin(2*np.pi*month_num/12),
        np.cos(2*np.pi*month_num/12),
    ])

results = {}
forecast_rows = []
fit_rows = []

for target in ["pm25", "pm10"]:
    sub = df.dropna(subset=[target]).copy()
    X = make_features(sub["month_index"].values, sub["month_num"].values)
    y = sub[target].values

    # Simple holdout validation (last 4 months) to report honest accuracy - not just training fit
    X_train, X_test = X[:-4], X[-4:]
    y_train, y_test = y[:-4], y[-4:]
    val_model = LinearRegression().fit(X_train, y_train)
    y_pred = val_model.predict(X_test)
    mae = round(mean_absolute_error(y_test, y_pred), 2)
    r2 = round(r2_score(y_test, y_pred), 3)

    # Final model trained on all available data for the actual forecast
    model = LinearRegression().fit(X, y)
    fitted = model.predict(X)
    for i, row in enumerate(sub.itertuples()):
        fit_rows.append({"target": target, "date": str(row.date.date()), "actual": row._asdict()[target] if False else getattr(row, target), "fitted": round(fitted[i],2)})

    last_idx = int(sub["month_index"].max())
    last_date = sub["date"].max()
    future_idx = np.arange(last_idx+1, last_idx+7)
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1,7)]
    future_month_num = [d.month for d in future_dates]
    Xf = make_features(future_idx, np.array(future_month_num))
    yf = model.predict(Xf)

    for d, val in zip(future_dates, yf):
        forecast_rows.append({"target": target, "date": str(d.date()), "forecast": round(float(val),2)})

    results[target] = {
        "coefficients": {"trend_per_month": round(model.coef_[0],4), "seasonal_sin": round(model.coef_[1],3), "seasonal_cos": round(model.coef_[2],3)},
        "intercept": round(model.intercept_,2),
        "holdout_MAE": mae, "holdout_R2": r2,
        "n_train_samples": len(y)
    }

pd.DataFrame(forecast_rows).to_csv("/home/claude/twin/05_analysis_ml/outputs/aqi_forecast_6month.csv", index=False)
pd.DataFrame(fit_rows).to_csv("/home/claude/twin/05_analysis_ml/outputs/aqi_model_fit_history.csv", index=False)
with open("/home/claude/twin/05_analysis_ml/outputs/aqi_model_metrics.json","w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
