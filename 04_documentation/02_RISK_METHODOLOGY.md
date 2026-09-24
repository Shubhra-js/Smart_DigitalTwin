# Infrastructure Risk/Stress Methodology (Substations)

## Why not ML
The substation dataset has no outage history, no load/fault records, and no
maintenance log — only static attributes (location, voltage class,
commission date). Any "predictive maintenance" or "failure probability" ML
model would need a labelled outcome to learn from (did this substation fail,
when). We don't have that, so training one would mean **inventing labels**,
which the brief explicitly rules out. Instead we built a transparent,
fully-documented **rule-based index** — every input and weight is visible
and justified below, and can be recalibrated the moment real outage data
becomes available (the same script structure would then support swapping in
a logistic regression or survival model).

## The formula
```
age_risk   = asset_age_years / max(asset_age_years across fleet)      # 0–1
tier_weight = 0.6 if 66kV "Distribution"  else 0.4 if 220/400kV "Transmission"
asset_risk_score = 0.7 × age_risk + 0.3 × tier_weight
```

- **Age term (70% weight):** older electromechanical/switchgear assets have
  statistically higher failure/maintenance rates industry-wide; age is the
  only condition proxy available in this dataset, so it gets the dominant
  weight.
- **Tier term (30% weight):** a 66kV distribution substation sits on the
  last mile to consumers, typically with less network redundancy than the
  meshed 220/400kV transmission backbone — so, all else equal, it is
  weighted as more consumer-critical. This is a **declared assumption**,
  not fitted from data (we have no outage data to fit it from).
- **Bands:** High ≥ 0.65, Medium ≥ 0.45, Low otherwise — chosen so the
  bands are roughly interpretable (High = old distribution assets; Low =
  newer, or transmission-tier, assets).
- **Missing commission dates (3 of 280 rows):** age_risk defaulted to the
  fleet median age_risk rather than 0 or 1, to avoid silently making an
  unknown-age asset look either falsely safe or falsely risky.

## Taluk-level rollup
`taluk_infrastructure_summary.csv` aggregates substation_count,
avg_asset_age, avg_risk_score, and % High-risk per taluk. This is presented
as an **infrastructure-coverage and condition proxy**, not a demand-supply
gap — the source data has no taluk-level electricity demand figures (demand
data is only available at whole-city level), so the twin does not claim to
know which taluk is electrically under-supplied, only which has the oldest
/ most distribution-heavy asset base. This limitation is stated explicitly
in `04_LIMITATIONS.md`.
