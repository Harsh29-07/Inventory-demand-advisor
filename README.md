# 📦 Inventory Demand Advisor

> **Forecast demand. Optimize reorder points. Simulate inventory. Reduce costs.**

A portfolio-grade analytics system that goes beyond simple forecasting — it turns demand predictions into actionable inventory decisions for small retailers.

---

## 🎯 What This Project Does

Most forecasting projects stop at "here's the predicted number." This system goes further:

1. **Forecasts** daily demand per SKU using multiple models (Baseline, Seasonal Naive, Prophet)
2. **Calculates** optimal reorder points and safety stock using service-level theory
3. **Simulates** day-by-day inventory under the policy, tracking stockouts and costs
4. **Compares** the optimized policy vs a naive shop-owner rule to quantify improvement

---

## 📁 Project Structure

```
inventory-demand-advisor/
│
├── data/
│   ├── raw/                   # Original train.csv (Kaggle)
│   └── processed/             # Cleaned processed_sales.csv
│
├── notebooks/
│   ├── 01_data_loading.ipynb  # Load, clean, sanity check
│   ├── 02_eda.ipynb           # Exploratory data analysis
│   ├── 03_forecasting.ipynb   # Model training & comparison
│   └── 04_inventory_simulation.ipynb  # Multi-SKU simulation
│
├── src/
│   └── inventory_simulator.py # Reusable reorder & simulation functions
│
├── reports/
│   └── business_case.md       # Business framing & results summary
│
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

**Kaggle — Store Item Demand Forecasting Challenge**

| Property | Value |
|---|---|
| Rows | 913,000 |
| Stores | 50 |
| Items (SKUs) | 50 |
| Date range | Jan 2013 – Dec 2017 |
| Granularity | Daily sales per store-item |

---

## 🔬 Methodology

### Step 1 — EDA
- Overall demand trend (upward + seasonal)
- Weekly and monthly seasonality patterns
- Demand distribution (right-skewed → safety stock needed)
- SKU-level Pareto analysis

### Step 2 — Forecasting
Three models evaluated on a 90-day hold-out test set:

| Model | Description |
|---|---|
| Baseline | Constant 7-day rolling average |
| Seasonal Naive | Repeats demand from same weekday |
| Prophet | Trend + weekly + yearly seasonality |

**Winner: Prophet** (lowest MAE and MAPE)

### Step 3 — Inventory Optimization
For each SKU:
- **Safety stock** = Z × σ(demand) × √(lead time)
- **Reorder point** = avg demand × lead time + safety stock
- **Order quantity** = avg demand × lead time (replenishment cycle)

Assuming 95% service level and 7-day supplier lead time.

### Step 4 — Simulation
Day-by-day simulation over the 90-day test period:
- Inventory decreases with demand each day
- Reorder triggered when inventory ≤ ROP
- Order arrives after lead time
- Stockouts and holding costs tracked daily

---

## 📈 Results

Simulation run on top 5 SKUs:

| Item | Reorder Point | Safety Stock | Stockouts | Total Cost |
|---|---|---|---|---|
| 15 | 7,101 | 955 | 13,431 | 312,834 |
| 28 | 7,091 | 954 | 13,588 | 324,412 |
| 13 | 6,805 | 916 | 12,320 | 302,124 |
| 18 | 6,805 | 919 | 12,653 | 306,102 |
| 25 | 6,517 | 882 | 11,935 | 292,169 |

*Holding cost = 1/unit/day | Stockout cost = 5/unit*

---

## 🛠 Tech Stack

- **Python** — pandas, numpy, scipy, matplotlib, seaborn
- **Prophet** — Meta's open-source forecasting library
- **scikit-learn** — MAE/MAPE evaluation
- **Jupyter** — notebooks for reproducible analysis

---

## 🚀 How to Run

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/inventory-demand-advisor.git
cd inventory-demand-advisor

# Install dependencies
pip install -r requirements.txt

# Download data from Kaggle
# https://www.kaggle.com/competitions/demand-forecasting-kernels-only
# Place train.csv in data/raw/

# Run notebooks in order
# 01 → 02 → 03 → 04
```

---

## 📌 Progress Log

| Day | Task | Status |
|---|---|---|
| 1 | Project setup & structure | ✅ |
| 2 | Data loading & cleaning | ✅ |
| 3 | EDA & business insights | ✅ |
| 4 | Baseline forecast model | ✅ |
| 5 | Prophet model & comparison | ✅ |
| 6 | Reorder logic & simulation | ✅ |
| 7 | Multi-SKU scaling | ✅ |

--
