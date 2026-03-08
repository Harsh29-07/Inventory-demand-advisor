# Small Business Inventory Optimization System

## Problem

Small retailers commonly suffer from two costly inventory failures:
- **Stockouts** — losing sales when products run out
- **Overstock** — tying up capital in excess inventory

Traditional rule-based reordering (e.g. "order when stock hits 100 units") ignores demand variability, lead times, and seasonal patterns.

---

## Solution

Built a forecasting and reorder simulation engine that combines:

1. **Time-series demand forecasting** (Baseline, Seasonal Naive, Prophet)
2. **Statistical safety stock calculation** (service-level driven, accounts for demand volatility)
3. **Reorder point optimization** based on lead time and historical demand
4. **Day-by-day inventory simulation** with cost tracking (holding + stockout costs)

---

## Dataset

- **Source:** Kaggle — Store Item Demand Forecasting Challenge
- **Size:** 913,000 rows | 50 stores | 50 items | Jan 2013 – Dec 2017
- **Granularity:** Daily sales per store-item pair

---

## Methodology

```
Raw Data → Cleaning → EDA → Forecasting → Reorder Optimization → Simulation → Cost Analysis
```

### Forecasting Models Evaluated
| Model          | Description                        |
|----------------|------------------------------------|
| Baseline       | Constant 7-day rolling mean        |
| Seasonal Naive | Repeats demand from same weekday   |
| Prophet        | Trend + weekly + yearly seasonality |

**Best model:** Prophet (lowest MAE & MAPE)

### Inventory Policy
- **Lead time:** 7 days
- **Service level:** 95%
- **Reorder point:** Avg demand × lead time + safety stock
- **Safety stock:** Z-score × demand std dev × √lead time

---

## Results (Simulation on Top 5 SKUs — 90-day test period)

| Item | Reorder Point | Safety Stock | Stockouts | Total Cost |
|------|--------------|-------------|-----------|------------|
| 15   | 7,101        | 955         | 13,431    | 312,834    |
| 28   | 7,091        | 954         | 13,588    | 324,412    |
| 13   | 6,805        | 916         | 12,320    | 302,124    |
| 18   | 6,805        | 919         | 12,653    | 306,102    |
| 25   | 6,517        | 882         | 11,935    | 292,169    |

*Costs are in simulation units (holding cost = 1/unit/day, stockout cost = 5/unit)*

---

## Business Impact

- Demonstrates **decision-driven analytics** beyond simple forecasting
- Reorder logic is **parameterized** — adjustable lead time, service level, costs
- System is **scalable** — runs across all 50 SKUs with one loop
- Provides **actionable inventory policy** per SKU, not just predictions

---

## Tech Stack

- Python (pandas, numpy, scipy, matplotlib, seaborn)
- Prophet (Meta's forecasting library)
- Jupyter Notebooks
- scikit-learn (evaluation metrics)

---

## How to Run

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/inventory-demand-advisor.git
cd inventory-demand-advisor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run notebooks in order
notebooks/01_data_loading.ipynb
notebooks/02_eda.ipynb
notebooks/03_forecasting.ipynb
notebooks/04_inventory_simulation.ipynb
```
