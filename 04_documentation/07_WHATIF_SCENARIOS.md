# What-If Scenario Design

All five levers live in the dashboard's **What-If Simulator** tab and run
client-side with fully visible formulas (shown under each result card as a
`formula:` caption). Baselines are pulled directly from the cleaned data —
none are invented.

## 1. LT consumer annual growth rate
- **Baseline:** 7.42%/yr (actual FY15→FY16 total LT+HT consumer growth)
- **Formula:** `projected = current_consumers × (1 + rate)^years`
- **City question it answers:** If Bengaluru's connection growth continues
  at the historical rate (or accelerates/slows), how many electricity
  connections will exist in N years, and does that growth rate look
  sustainable against the existing distribution-substation base shown in
  the Infrastructure tab?

## 2. Projection horizon (years)
- Multiplies through scenarios 1 and the energy-requirement projection.

## 3. Target distribution loss %
- **Baseline:** 12.03% (actual FY15-16 distribution loss)
- **Formula:** `energy_saved_MU = projected_energy_requirement × (baseline_loss% − target_loss%) / 100`
  `cost_saved = energy_saved_MU × ₹/unit (reference rate from RE purchase table, ₹4.15) `
- **City question it answers:** What's the energy and cost payoff of
  distribution-network investment (transformer upgrades, feeder
  segregation, theft reduction) that brings losses down toward the
  originally-approved 13.4%→lower target?
- **Caveat shown on dashboard:** the ₹/unit figure is BESCOM's *renewable
  purchase* blended rate, used here only as an order-of-magnitude cost
  proxy — not the true avoided cost of loss (which would depend on the
  marginal generation source), so it is explicitly labelled "reference
  rate, proxy."

## 4. Solar share of renewable purchase
- **Baseline:** 3.4% (solar MU ÷ total RE MU purchased, 2015-16)
- **Formula:** `solar_MU = total_RE_MU_baseline × solar_share%`
- **City question it answers:** What would a policy push toward solar (vs
  wind/biomass/hydel, which dominate the current 2015-16 mix) look like in
  absolute MU terms, holding total RE purchase constant?

## 5. % of High/Medium-risk substations upgraded
- **Baseline:** 0% (no upgrades)
- **Formula:** `remaining_at_risk = (High+Medium count) × (1 − upgraded%)`
- **City question it answers:** How much of a capital renewal programme
  (replacing ageing distribution-tier assets first, per the risk
  methodology) is needed to bring the network's risk profile down, and
  which taluks should be prioritised (cross-referenced against the
  Infrastructure tab's taluk risk ranking)?

## What was deliberately NOT simulated
- **Air-quality what-if** (e.g. "what if PM2.5 dropped 20% due to EV
  adoption") was considered but **excluded**: the AQ forecast model's own
  holdout R² is negative (see model card), so layering a second speculative
  scenario on top of an already low-confidence forecast would compound
  unsupported claims. The Air Quality tab stays descriptive + forecast-only.
