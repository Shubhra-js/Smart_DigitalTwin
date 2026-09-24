"""
Stage: Smart-City Indicators -> Risk/Stress Assessment (Infrastructure layer)
Why NOT ML here: we have no failure/outage history for the 280 substations,
so there is no valid target label to train or validate a predictive model on.
Training an ML classifier on invented labels would be unsupported and
non-explainable. Instead we build a transparent, documented RULE-BASED
risk index from the two attributes the data actually gives us: asset age
and voltage tier. Every weight is stated explicitly below (no hidden ML).
"""
import pandas as pd, numpy as np

df = pd.read_csv("/home/claude/twin/02_cleaned_data/substations_cleaned.csv")

# --- Age risk (0-1): normalised age against the oldest asset in the fleet ---
max_age = df["asset_age_years"].max()
df["age_risk"] = (df["asset_age_years"] / max_age).round(3)
# Assets with unknown commission date -> use fleet-median age risk (documented, conservative default; NOT invented data)
median_risk = df["age_risk"].median()
df["age_risk"] = df["age_risk"].fillna(median_risk)

# --- Criticality weight by voltage tier ---
# 66kV Distribution substations sit closest to the consumer (last-mile), so an
# outage there directly interrupts local supply -> weighted higher (0.6).
# 220/400kV Transmission substations are fewer, and the grid is normally
# meshed/redundant at that level -> weighted 0.4 for this index. These weights
# are declared assumptions, stated for transparency, not derived from outage data.
df["tier_weight"] = np.where(df["infrastructure_tier"] == "Distribution (66kV)", 0.6, 0.4)

df["asset_risk_score"] = (0.7 * df["age_risk"] + 0.3 * df["tier_weight"]).round(3)

def band(s):
    if s >= 0.65: return "High"
    if s >= 0.45: return "Medium"
    return "Low"
df["risk_band"] = df["asset_risk_score"].apply(band)

df.to_csv("/home/claude/twin/05_analysis_ml/outputs/substation_risk_scored.csv", index=False)

# --- Taluk-level rollup: infrastructure coverage + average asset risk ---
taluk = df.groupby(["district","taluk"]).agg(
    substation_count=("substation_id","count"),
    avg_asset_age=("asset_age_years","mean"),
    pct_high_risk=("risk_band", lambda s: round((s=="High").mean()*100,1)),
    avg_risk_score=("asset_risk_score","mean"),
    distribution_substations=("infrastructure_tier", lambda s: (s=="Distribution (66kV)").sum()),
    transmission_substations=("infrastructure_tier", lambda s: (s=="Transmission (EHV)").sum()),
).reset_index()
taluk["avg_asset_age"] = taluk["avg_asset_age"].round(1)
taluk["avg_risk_score"] = taluk["avg_risk_score"].round(3)
taluk.to_csv("/home/claude/twin/05_analysis_ml/outputs/taluk_infrastructure_summary.csv", index=False)

print("Risk scoring complete.")
print(df["risk_band"].value_counts())
print(taluk.sort_values("avg_risk_score", ascending=False).head(8))
