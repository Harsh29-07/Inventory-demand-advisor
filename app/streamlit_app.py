"""
app/streamlit_app.py
--------------------
Inventory Demand Advisor — Interactive Dashboard
Run with: streamlit run app/streamlit_app.py
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from src.inventory_simulator import calculate_reorder_point, simulate_inventory

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Inventory Demand Advisor",
    page_icon="📦",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f1117;
    color: #e8e8e8;
}

.metric-card {
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.metric-label {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 6px;
    font-family: 'DM Mono', monospace;
}
.metric-value {
    font-size: 1.9rem;
    font-weight: 600;
    color: #f0f0f0;
    line-height: 1;
}
.metric-sub {
    font-size: 0.78rem;
    color: #6b7280;
    margin-top: 4px;
}

.section-header {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4ade80;
    font-family: 'DM Mono', monospace;
    margin-bottom: 4px;
}

h1 { font-weight: 600 !important; font-size: 1.8rem !important; }
h2 { font-weight: 400 !important; font-size: 1.1rem !important; color: #9ca3af !important; }

.stSelectbox label, .stSlider label { color: #9ca3af !important; font-size: 0.85rem !important; }

div[data-testid="stSidebar"] {
    background: #13161f;
    border-right: 1px solid #1e2130;
}
</style>
""", unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'processed_sales.csv')
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Aggregate by item across all stores
@st.cache_data
def get_item_series(item_id):
    return (df[df['item'] == item_id]
            .groupby('date', as_index=False)['sales']
            .sum()
            .sort_values('date')
            .reset_index(drop=True))

all_items = sorted(df['item'].unique())
top_5 = (df.groupby('item')['sales'].sum()
           .sort_values(ascending=False)
           .head(5)
           .index.tolist())


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Inventory Advisor")
    st.markdown("---")

    st.markdown('<p class="section-header">SKU Selection</p>', unsafe_allow_html=True)
    selected_item = st.selectbox(
        "Select Item",
        options=all_items,
        index=all_items.index(top_5[0]),
        format_func=lambda x: f"Item {x}{'  ★ top 5' if x in top_5 else ''}"
    )

    st.markdown("---")
    st.markdown('<p class="section-header">Policy Parameters</p>', unsafe_allow_html=True)

    lead_time = st.slider("Lead Time (days)", 1, 21, 7)
    service_level = st.slider("Service Level (%)", 80, 99, 95) / 100
    initial_inv = st.slider("Starting Inventory", 50, 500, 200, step=25)
    holding_cost = st.slider("Holding Cost / unit / day", 1, 10, 1)
    stockout_cost = st.slider("Stockout Cost / unit", 1, 20, 5)

    st.markdown("---")
    st.caption("Data: Kaggle Store Item Demand · 5yr · 50 SKUs")


# ── Compute ───────────────────────────────────────────────────
sku_df = get_item_series(selected_item)
train  = sku_df.iloc[:-90].copy()
test   = sku_df.iloc[-90:].copy().reset_index(drop=True)

reorder_point, safety_stock = calculate_reorder_point(train, lead_time, service_level)
order_qty = int(train['sales'].mean() * lead_time)

result = simulate_inventory(
    test,
    reorder_point=reorder_point,
    order_quantity=order_qty,
    initial_inventory=initial_inv,
    lead_time=lead_time,
    holding_cost_per_unit=holding_cost,
    stockout_cost_per_unit=stockout_cost,
)

# Baseline forecast
last_n_avg = train['sales'].tail(7).mean()
test['forecast'] = last_n_avg

# ── Header ────────────────────────────────────────────────────
st.markdown(f"# Item {selected_item} — Inventory Dashboard")
st.markdown(f"Showing 90-day simulation · Lead time {lead_time}d · {int(service_level*100)}% service level")
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Reorder Point</div>
        <div class="metric-value">{reorder_point:,.0f}</div>
        <div class="metric-sub">units</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Safety Stock</div>
        <div class="metric-value">{safety_stock:,.0f}</div>
        <div class="metric-sub">units</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Stockouts</div>
        <div class="metric-value" style="color:#f87171">{result['stockouts']:,.0f}</div>
        <div class="metric-sub">units lost</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Holding Cost</div>
        <div class="metric-value">{result['holding_cost']:,.0f}</div>
        <div class="metric-sub">simulation units</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Cost</div>
        <div class="metric-value" style="color:#facc15">{result['total_cost']:,.0f}</div>
        <div class="metric-sub">holding + stockout</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────
DARK_BG   = "#0f1117"
CARD_BG   = "#1a1d27"
GRID_COL  = "#22253a"
TEXT_COL  = "#9ca3af"
GREEN     = "#4ade80"
BLUE      = "#60a5fa"
RED       = "#f87171"
YELLOW    = "#facc15"

def dark_fig(figsize=(12, 3.5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=8)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.grid(axis='y', color=GRID_COL, linewidth=0.6, linestyle='--')
    ax.grid(axis='x', visible=False)
    return fig, ax


col_left, col_right = st.columns(2)

# ── Chart 1: Forecast ─────────────────────────────────────────
with col_left:
    st.markdown('<p class="section-header">Demand Forecast vs Actual</p>', unsafe_allow_html=True)
    fig, ax = dark_fig()
    ax.plot(test['date'], test['sales'],    color=BLUE,  linewidth=1.4, label='Actual', alpha=0.9)
    ax.plot(test['date'], test['forecast'], color=GREEN, linewidth=1.4, label='Forecast (7d avg)',
            linestyle='--', alpha=0.85)
    ax.fill_between(test['date'], test['sales'], test['forecast'],
                    alpha=0.08, color=GREEN)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL, fontsize=8)
    ax.set_ylabel("Daily Sales", color=TEXT_COL, fontsize=8)
    mape = np.mean(np.abs((test['sales'] - test['forecast']) / test['sales'])) * 100
    mae  = np.mean(np.abs(test['sales'] - test['forecast']))
    ax.set_title(f"MAE: {mae:.1f}  ·  MAPE: {mape:.1f}%", color=TEXT_COL, fontsize=8, pad=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Chart 2: Inventory Level ──────────────────────────────────
with col_right:
    st.markdown('<p class="section-header">Inventory Level Over Time</p>', unsafe_allow_html=True)
    fig, ax = dark_fig()
    ax.plot(test['date'], result['inventory_history'], color=BLUE, linewidth=1.4, label='Inventory')
    ax.axhline(reorder_point, color=RED,    linestyle='--', linewidth=1.1,
               label=f'ROP ({reorder_point:,.0f})')
    ax.axhline(safety_stock,  color=YELLOW, linestyle=':',  linewidth=1.1,
               label=f'Safety Stock ({safety_stock:,.0f})')
    ax.fill_between(test['date'], 0, result['inventory_history'],
                    alpha=0.08, color=BLUE)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL, fontsize=8)
    ax.set_ylabel("Units in Stock", color=TEXT_COL, fontsize=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("<br>", unsafe_allow_html=True)

# ── Summary Table: all top 5 ──────────────────────────────────
st.markdown('<p class="section-header">Top 5 SKU Summary</p>', unsafe_allow_html=True)

@st.cache_data
def build_summary(lead_time, service_level, initial_inv, holding_cost, stockout_cost):
    rows = []
    for item in top_5:
        s = get_item_series(item)
        tr = s.iloc[:-90]
        te = s.iloc[-90:].reset_index(drop=True)
        rop, ss = calculate_reorder_point(tr, lead_time, service_level)
        oq = int(tr['sales'].mean() * lead_time)
        res = simulate_inventory(te, rop, oq, initial_inv, lead_time, holding_cost, stockout_cost)
        rows.append({
            "Item":           f"Item {item}",
            "Avg Daily Sales": round(tr['sales'].mean(), 1),
            "Reorder Point":  round(rop, 0),
            "Safety Stock":   round(ss, 0),
            "Order Qty":      oq,
            "Stockouts":      round(res['stockouts']),
            "Holding Cost":   res['holding_cost'],
            "Stockout Cost":  res['stockout_cost'],
            "Total Cost":     res['total_cost'],
        })
    return pd.DataFrame(rows)

summary_df = build_summary(lead_time, service_level, initial_inv, holding_cost, stockout_cost)

# Highlight selected item
def highlight_selected(row):
    if row['Item'] == f"Item {selected_item}":
        return ['background-color: #1e3a2a; color: #4ade80'] * len(row)
    return [''] * len(row)

styled = (summary_df.style
          .apply(highlight_selected, axis=1)
          .format({
              "Avg Daily Sales": "{:.1f}",
              "Reorder Point":   "{:,.0f}",
              "Safety Stock":    "{:,.0f}",
              "Order Qty":       "{:,.0f}",
              "Stockouts":       "{:,.0f}",
              "Holding Cost":    "{:,.0f}",
              "Stockout Cost":   "{:,.0f}",
              "Total Cost":      "{:,.0f}",
          }))

st.dataframe(styled, use_container_width=True, height=230)

st.markdown("<br>", unsafe_allow_html=True)

# ── Cost Breakdown Bar ────────────────────────────────────────
st.markdown('<p class="section-header">Cost Breakdown — Top 5 SKUs</p>', unsafe_allow_html=True)

fig, ax = dark_fig(figsize=(12, 3.2))
x     = np.arange(len(top_5))
width = 0.35

bars1 = ax.bar(x - width/2, summary_df['Holding Cost'],   width, color=BLUE,   alpha=0.85, label='Holding Cost')
bars2 = ax.bar(x + width/2, summary_df['Stockout Cost'],  width, color=RED,    alpha=0.85, label='Stockout Cost')

ax.set_xticks(x)
ax.set_xticklabels([f"Item {i}" for i in top_5], color=TEXT_COL, fontsize=9)
ax.legend(facecolor=CARD_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL, fontsize=8)
ax.set_ylabel("Cost", color=TEXT_COL, fontsize=8)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
            f"{bar.get_height():,.0f}", ha='center', va='bottom', color=TEXT_COL, fontsize=7)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
            f"{bar.get_height():,.0f}", ha='center', va='bottom', color=TEXT_COL, fontsize=7)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")
st.caption("Inventory Demand Advisor · Portfolio Project · Data: Kaggle Store Item Demand Forecasting")
