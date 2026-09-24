import pandas as pd, json, numpy as np

OUT = "/home/claude/twin/05_analysis_ml/outputs"
CLEAN = "/home/claude/twin/02_cleaned_data"
REF = "/home/claude/twin/03_curated_reference_data"

sub = pd.read_csv(f"{OUT}/substation_risk_scored.csv")
taluk = pd.read_csv(f"{OUT}/taluk_infrastructure_summary.csv")
centroids = pd.read_csv(f"{REF}/taluk_centroids_curated.csv")
aqi = pd.read_csv(f"{CLEAN}/air_quality_cleaned.csv")
aqi_fc = pd.read_csv(f"{OUT}/aqi_forecast_6month.csv")
aqi_fit = pd.read_csv(f"{OUT}/aqi_model_fit_history.csv")
aqi_metrics = json.load(open(f"{OUT}/aqi_model_metrics.json"))
energy_req = pd.read_csv(f"{CLEAN}/energy_requirement_cleaned.csv")
consumers = pd.read_csv(f"{CLEAN}/consumers_cleaned.csv")
units = pd.read_csv(f"{CLEAN}/units_sold_cleaned.csv")
opratio = pd.read_csv(f"{CLEAN}/operating_ratio_cleaned.csv")
re_purchase = pd.read_csv(f"{CLEAN}/re_purchase_cleaned.csv")
cpcb = pd.read_csv(f"{REF}/aqi_category_reference_CPCB.csv")

taluk = taluk.merge(centroids, on=["district","taluk"], how="left")

# jitter substation points around their taluk centroid (schematic map, not GPS-accurate)
rng = np.random.default_rng(42)
sub = sub.merge(centroids, on=["district","taluk"], how="left")
sub["map_lat"] = sub["approx_lat"] + rng.uniform(-0.025,0.025,len(sub))
sub["map_lon"] = sub["approx_lon"] + rng.uniform(-0.025,0.025,len(sub))

def total_row(df, col_metric, val):
    r = df[df[col_metric]==val]
    return None if r.empty else r.iloc[0].to_dict()

data = {
    "meta": {
        "reference_year": 2026,
        "note": "All figures are derived only from the supplied BESCOM/AQI datasets, except items explicitly flagged 'curated' or 'reference' (map centroids, CPCB AQI bands)."
    },
    "energy_requirement": energy_req.to_dict(orient="records"),
    "consumers": consumers.to_dict(orient="records"),
    "units_sold": units.to_dict(orient="records"),
    "operating_ratio": opratio.to_dict(orient="records"),
    "re_purchase": re_purchase.to_dict(orient="records"),
    "substations": sub[["substation_id","district","taluk","substation_name","voltage_kv","commission_year",
                          "asset_age_years","infrastructure_tier","asset_risk_score","risk_band","map_lat","map_lon"]].to_dict(orient="records"),
    "taluk_summary": taluk.to_dict(orient="records"),
    "aqi_monthly": aqi.to_dict(orient="records"),
    "aqi_forecast": aqi_fc.to_dict(orient="records"),
    "aqi_fit": aqi_fit.to_dict(orient="records"),
    "aqi_model_metrics": aqi_metrics,
    "cpcb_bands": cpcb.to_dict(orient="records"),
}

with open("/home/claude/twin/06_dashboard/dashboard_data.json","w") as f:
    json.dump(data, f, indent=0, default=str)

print("Dashboard dataset built:", len(json.dumps(data)), "bytes")
print("Substations:", len(data["substations"]), "| Taluks:", len(data["taluk_summary"]), "| AQI months:", len(data["aqi_monthly"]))
