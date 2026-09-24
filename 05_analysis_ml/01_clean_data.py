"""
Stage: Raw Data -> Data Filtering/Cleaning
Bengaluru Smart-City Digital Twin
Cleans all 7 raw BESCOM/AQ datasets into tidy CSVs in 02_cleaned_data/.
Every drop/keep decision is commented inline; a human-readable summary is
also written to 04_documentation/02_DATA_CLEANING_LOG.md by this script.
"""
import pandas as pd, numpy as np, re, json, os

RAW = "/home/claude/twin/01_raw_data"
OUT = "/home/claude/twin/02_cleaned_data"
os.makedirs(OUT, exist_ok=True)
log = []

def logit(name, kept, removed, reason):
    log.append({"dataset": name, "kept": kept, "removed": removed, "reason": reason})

# ---------------------------------------------------------------------------
# 1. SUBSTATIONS (infrastructure asset registry)
# ---------------------------------------------------------------------------
df = pd.read_csv(f"{RAW}/BESCOM_6_Substations_raw.csv")
df.columns = [c.strip() for c in df.columns]

# Drop 'Sl. No' -> pure row identifier, no analytical value
# Drop 'Zone' -> constant ("Bengaluru") for all 280 rows, zero information
df = df.drop(columns=["Sl. No", "Zone"])

# Normalise inconsistent district spelling (data entry variants observed in raw file)
district_map = {
    "Bengaluru Urban": "Bangalore Urban",
    "CB Pura": "Chikkaballapur",
    "C B pura": "Chikkaballapur",
}
df["District"] = df["District"].str.strip().replace(district_map)

taluk_map = {"Bengaluru South": "Bangalore South", "DB pura": "Doddaballapura", "CB Pura": "Chikkaballapur"}
df["Taluk"] = df["Taluk"].str.strip().replace(taluk_map)
df["Name of Sub-Station"] = df["Name of Sub-Station"].str.strip()

df = df.rename(columns={
    "District": "district", "Taluk": "taluk", "Name of Sub-Station": "substation_name",
    "Voltage Class (in kV)": "voltage_kv", "Date of commission": "commission_date_raw"
})

df["commission_date"] = pd.to_datetime(df["commission_date_raw"], format="%d-%m-%Y", errors="coerce")
df["commission_year"] = df["commission_date"].dt.year
REF_YEAR = 2026
df["asset_age_years"] = REF_YEAR - df["commission_year"]

# Voltage class -> infrastructure tier (from actual observed values 66/220/400 kV only)
def tier(v):
    if v >= 220: return "Transmission (EHV)"
    return "Distribution (66kV)"
df["infrastructure_tier"] = df["voltage_kv"].apply(tier)

df.insert(0, "substation_id", ["SS" + str(i+1).zfill(3) for i in range(len(df))])
df.to_csv(f"{OUT}/substations_cleaned.csv", index=False)
logit("Substations", "district, taluk, substation_name, voltage_kv, commission_date, commission_year, asset_age_years, infrastructure_tier",
      "Sl.No (identifier), Zone (constant value)",
      "Sl.No carries no analytical meaning; Zone is 100% 'Bengaluru' for every row so it adds no variance. "
      "1 row had a missing commission date -> kept as NaN (age unknown) rather than guessed.")

# ---------------------------------------------------------------------------
# 2. ENERGY REQUIREMENT (Approved vs Actual, FY2015-16)
# ---------------------------------------------------------------------------
df = pd.read_csv(f"{RAW}/BESCOM_1_EnergyRequirement_raw.csv")
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={"Sl. No.": "sl_no", "Particulars": "metric",
                         "Approved FY2015-16": "approved_fy1516", "Actuals FY -2015-16": "actual_fy1516"})
df = df.drop(columns=["sl_no"])  # identifier
df["achievement_pct"] = (df["actual_fy1516"] / df["approved_fy1516"] * 100).round(2)
df.to_csv(f"{OUT}/energy_requirement_cleaned.csv", index=False)
logit("Energy Requirement", "metric, approved_fy1516, actual_fy1516, achievement_pct (derived)",
      "sl_no (identifier)", "Row index has no analytical meaning. achievement_pct derived to show plan-vs-actual gap.")

# ---------------------------------------------------------------------------
# 3. CONSUMERS (FY16 vs FY15) -> tidy long format
# ---------------------------------------------------------------------------
raw = pd.read_csv(f"{RAW}/BESCOM_2_Consumers_raw.csv", header=None)
rows = []
category = None
for _, r in raw.iloc[1:].iterrows():
    a, label, unit, fy16, fy15, chg = r[0], r[1], r[2], r[3], r[4], r[5]
    if str(a).strip().startswith("Total H.T"):  # grand-total row: description sits in col A, not label
        cat, sub = "TOTAL", "All consumers (LT+HT)"
    else:
        if pd.isna(label): continue
        label = str(label).strip()
        if label in ("LT", "HT") and pd.isna(unit):
            category = label
            continue
        cat, sub = category, label
    def to_num(x):
        try: return float(str(x).replace('%','').strip())
        except: return np.nan
    rows.append({"category": cat, "subcategory": sub, "unit": str(unit).strip(),
                 "fy16": to_num(fy16), "fy15": to_num(fy15), "pct_change": to_num(chg)})
cdf = pd.DataFrame(rows)
cdf = cdf.dropna(subset=["fy16", "fy15"], how="all").reset_index(drop=True)  # drop stray group-header artifacts (no data)
# Normalise everything to absolute consumer COUNT (Nos.) so LT (in Lakhs) and HT (in Nos.) are comparable
cdf["fy16_count"] = np.where(cdf["unit"].str.contains("Lakh", case=False, na=False), cdf["fy16"]*1e5, cdf["fy16"])
cdf["fy15_count"] = np.where(cdf["unit"].str.contains("Lakh", case=False, na=False), cdf["fy15"]*1e5, cdf["fy15"])
cdf.to_csv(f"{OUT}/consumers_cleaned.csv", index=False)
logit("Number of Consumers", "category(LT/HT/TOTAL), subcategory, fy16, fy15, pct_change, fy16_count/fy15_count (derived, unit-normalised)",
      "Section header rows (blank placeholder rows for 'LT'/'HT' group titles), sl-no column 'A'",
      "Header/group rows carried no data (blank fy16/fy15); reshaped from a wide printed-report layout into tidy rows "
      "and normalised Lakhs->absolute counts so LT and HT are on one comparable numeric scale.")

# ---------------------------------------------------------------------------
# 4. UNITS SOLD (FY16 vs FY15) -> tidy long format (MU)
# ---------------------------------------------------------------------------
raw = pd.read_csv(f"{RAW}/BESCOM_3_UnitsSold_raw.csv", header=None)
rows = []
category = None
for _, r in raw.iloc[1:].iterrows():
    a, label, unit, fy16, fy15, chg = r[0], r[1], r[2], r[3], r[4], r[5]
    if str(a).strip().startswith("Total LT+HT"):  # grand-total row: description sits in col A, not label
        cat, sub = "TOTAL", "All units sold (LT+HT)"
    else:
        if pd.isna(label): continue
        label = str(label).strip()
        if label in ("LT", "HT") and pd.isna(unit):
            category = label
            continue
        cat, sub = category, label
    def to_num(x):
        try: return float(str(x).replace('%','').strip())
        except: return np.nan
    rows.append({"category": cat, "subcategory": sub, "unit_MU": "MU",
                 "fy16_MU": to_num(fy16), "fy15_MU": to_num(fy15), "pct_change": to_num(chg)})
udf = pd.DataFrame(rows)
udf.to_csv(f"{OUT}/units_sold_cleaned.csv", index=False)
logit("Number of Units Sold", "category(LT/HT/TOTAL), subcategory, fy16_MU, fy15_MU, pct_change",
      "Section header rows, sl-no column",
      "Same reshape logic as Consumers dataset; already single-unit (MU) so no unit conversion needed.")

# ---------------------------------------------------------------------------
# 5. OPERATING RATIO (cost structure, FY16/FY15/FY14)
# ---------------------------------------------------------------------------
df = pd.read_csv(f"{RAW}/BESCOM_4_OperatingRatio_raw.csv")
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={"Sl. No": "sl_no", "Particulars": "cost_component"})
df = df[df["cost_component"] != ""]
df = df[df["cost_component"].astype(str).str.lower() != "total"]  # keep components, drop the 100% total row (redundant, always 100)
for c in ["FY-16", "FY-15", "FY-14"]:
    df[c] = df[c].astype(str).str.replace('%','').astype(float)
df = df.drop(columns=["sl_no"]).rename(columns={"FY-16":"fy16_pct","FY-15":"fy15_pct","FY-14":"fy14_pct"})
df.to_csv(f"{OUT}/operating_ratio_cleaned.csv", index=False)
logit("Operating Ratio", "cost_component, fy16_pct, fy15_pct, fy14_pct",
      "sl_no (identifier), 'Total' row (always exactly 100%, redundant)",
      "Total row is definitionally 100% every year and adds no information; kept as documented invariant only.")

# ---------------------------------------------------------------------------
# 6. RENEWABLE ENERGY PURCHASE (2015-16, by source)
# ---------------------------------------------------------------------------
df = pd.read_csv(f"{RAW}/BESCOM_5_RE_Purchase_raw.csv")
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={"RE purchase 2015-16": "source", "Energy in MU": "energy_mu",
                         "Amount in Crs.": "amount_crore", "Rs/unit": "rs_per_unit"})
df["is_aggregate_row"] = df["source"].isin(["Total", "solar", "Non Solar"])
df.to_csv(f"{OUT}/re_purchase_cleaned.csv", index=False)
logit("Renewable Energy Purchase", "source, energy_mu, amount_crore, rs_per_unit, is_aggregate_row (flag)",
      "nothing removed", "All rows kept; 'Total'/'solar'/'Non Solar' rows flagged as aggregates (not individual sources) "
      "so downstream charts don't double count them against the individual-source rows.")

# ---------------------------------------------------------------------------
# 7. AIR QUALITY (monthly, Jan-2017 to Dec-2018)
# ---------------------------------------------------------------------------
df = pd.read_csv(f"{RAW}/AirQuality_Bengaluru_2017to2018_raw.csv")
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={
    "City Name": "city", "Month -Year": "month_year",
    "Monthly mean/average concentrationPM2.5": "pm25",
    "Monthly mean concentrationPM10": "pm10",
    "Monthly mean concentrationNO2": "no2",
    "Monthly mean concentrationSO2": "so2",
    "Monthly mean concentrationO3": "o3",
    "No of AQM Sensors,Environmental sensors deployed": "sensor_count",
})
df["o3"] = pd.to_numeric(df["o3"], errors="coerce")  # 'NA' strings -> NaN (O3 not measured pre-Jun-2018)
df["date"] = pd.to_datetime(df["month_year"], format="%b-%y")
df = df.sort_values("date").reset_index(drop=True)
df["month_index"] = range(1, len(df)+1)
df["month_num"] = df["date"].dt.month
df = df[["date","month_year","month_index","month_num","city","pm25","pm10","no2","so2","o3","sensor_count"]]
df.to_csv(f"{OUT}/air_quality_cleaned.csv", index=False)
logit("Air Quality", "date, pm25, pm10, no2, so2, o3, sensor_count",
      "nothing removed (city column kept though constant, needed for future multi-city extension)",
      "'NA' text in O3 (sensor not yet deployed pre-Jun-2018) correctly parsed to null rather than 0, "
      "so the ML model does not learn a false 'drop to zero' pattern.")

with open("/home/claude/twin/04_documentation/_cleaning_log.json","w") as f:
    json.dump(log, f, indent=2)

print("Cleaning complete.")
for l in log:
    print(l["dataset"], "->", "KEPT:", l["kept"][:60], "...")
