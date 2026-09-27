from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Commercial Market Opportunity Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
        .block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 2rem; }
        .dashboard-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; }
        .dashboard-subtitle { font-size: 1rem; color: #6B7280; margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True
)

# --- PATHS & DATA LOADING ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

@st.cache_data(show_spinner=False)
def load_dashboard_data():
    for f in ["scorecard.parquet", "economics.parquet", "heatmap.parquet"]:
        if not (DATA_DIR / f).exists():
            st.error(f"Missing {f}. Run python scripts/collect_data.py")
            st.stop()
    return (
        pd.read_parquet(DATA_DIR / "scorecard.parquet"),
        pd.read_parquet(DATA_DIR / "economics.parquet"),
        pd.read_parquet(DATA_DIR / "heatmap.parquet")
    )

scorecard_raw, economics_raw, heatmap_df = load_dashboard_data()

# --- HEADER & FUNCTIONAL FILTERS ---
st.markdown('<div class="dashboard-title">Where should TellCo focus?</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Commercial off-grid and distributed markets, scored for diesel-dependent private customers.</div>', unsafe_allow_html=True)

f1, f2, f3, f4, f5 = st.columns(5)
selected_sector = f1.selectbox("Sector", ["All", "Mining", "Hospitality", "Agro-Export", "Grid-tied C&I"])
selected_conn = f2.selectbox("Connection", ["All", "Off-grid", "Weak grid / hybrid", "Grid-tied"])
selected_model = f3.selectbox("Model", ["All", "A - Sale", "B - Lease", "C - EaaS"])
selected_size = f4.selectbox("Deal size", ["30 kWp - 2 MWp", "> 2 MWp"])
selected_weights = f5.selectbox("Weights", ["Base case", "High currency risk", "Low finance access"])

st.markdown("---")

# --- DYNAMIC DATA PROCESSING ---
# 1. Dynamic Weight Calculation
weight_scenarios = {
    "Base case": {"OFFTAKERS": 0.20, "ECONOMICS": 0.15, "RECURRING_FIT": 0.15, "CURRENCY": 0.15, "REGULATION": 0.10, "FINANCE": 0.10, "POLITICAL": 0.10, "RIGHT_TO_WIN": 0.05},
    "High currency risk": {"OFFTAKERS": 0.18, "ECONOMICS": 0.12, "RECURRING_FIT": 0.15, "CURRENCY": 0.25, "REGULATION": 0.10, "FINANCE": 0.10, "POLITICAL": 0.05, "RIGHT_TO_WIN": 0.05},
    "Low finance access": {"OFFTAKERS": 0.20, "ECONOMICS": 0.15, "RECURRING_FIT": 0.10, "CURRENCY": 0.15, "REGULATION": 0.10, "FINANCE": 0.20, "POLITICAL": 0.05, "RIGHT_TO_WIN": 0.05}
}

w = weight_scenarios[selected_weights]
scorecard_df = scorecard_raw.copy()
scorecard_df["WEIGHTED TOTAL"] = (
    scorecard_df["OFFTAKERS"] * w["OFFTAKERS"] + scorecard_df["ECONOMICS"] * w["ECONOMICS"] +
    scorecard_df["RECURRING_FIT"] * w["RECURRING_FIT"] + scorecard_df["CURRENCY"] * w["CURRENCY"] +
    scorecard_df["REGULATION"] * w["REGULATION"] + scorecard_df["FINANCE"] * w["FINANCE"] +
    scorecard_df["POLITICAL"] * w["POLITICAL"] + scorecard_df["RIGHT_TO_WIN"] * w["RIGHT_TO_WIN"]
)

# 2. Sector Filtering
if selected_sector != "All":
    valid_markets = heatmap_df[heatmap_df[selected_sector].isin(["Priority", "Priority - verify data", "Secondary"])]["MARKET"]
    scorecard_df = scorecard_df[scorecard_df["MARKET"].isin(valid_markets)]

scorecard_df = scorecard_df.sort_values("WEIGHTED TOTAL", ascending=False).reset_index(drop=True)
scorecard_df.insert(0, "RANK", scorecard_df.index + 1)

# 3. Connection Filtering
economics_df = economics_raw.copy()
if selected_conn != "All":
    economics_df = economics_df[economics_df["Connection"] == selected_conn]
economics_df = economics_df.sort_values("Avoided Cost", ascending=False)

# --- NAVIGATION TABS ---
tab1, tab2 = st.tabs(["1 · Where to focus", "2 · Why and which sector"])

# === VIEW 1: WHERE TO FOCUS ===
with tab1:
    col_map, col_seq = st.columns([2.5, 1])
    
    with col_map:
        if scorecard_df.empty:
            st.warning("No markets match the selected filter combination.")
        else:
            fig_map = px.scatter_geo(
                scorecard_df, locations="MARKET", locationmode="country names", 
                size="WEIGHTED TOTAL", color="WEIGHTED TOTAL", hover_name="MARKET",
                color_continuous_scale="Teal", projection="natural earth"
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400)
            st.plotly_chart(fig_map, use_container_width=True)
        
    with col_seq:
        st.markdown("**Dynamic Entry Sequence**")
        if not scorecard_df.empty:
            for idx, row in scorecard_df.head(5).iterrows():
                st.markdown(f"**{row['RANK']}. {row['MARKET']}** (Score: {row['WEIGHTED TOTAL']:.2f})<br><span style='color:#6B7280; font-size:0.85rem;'>Lead: {row['LEAD MODEL']}</span>", unsafe_allow_html=True)
            if selected_weights == "High currency risk":
                st.info("Notice Zambia drops to 5th place or lower due to the 25% currency risk weighting penalty.")
            else:
                st.caption("Sequence dynamically recalculates based on filters.")

    st.dataframe(
        scorecard_df.style.background_gradient(subset=['WEIGHTED TOTAL'], cmap='Spectral').format({'WEIGHTED TOTAL': '{:.2f}'}),
        use_container_width=True, hide_index=True
    )

# === VIEW 2: WHY AND WHICH SECTOR ===
with tab2:
    c_chart, c_metrics = st.columns([3, 1])
    
    with c_chart:
        fig = go.Figure()
        if not economics_df.empty:
            fig.add_trace(go.Bar(
                y=economics_df["Site"], x=economics_df["Avoided Cost"],
                orientation='h', name="Avoided Cost (Diesel/Tariff)",
                marker=dict(color="#B45309"), width=0.3
            ))
            for i, row in economics_df.iterrows():
                fig.add_trace(go.Scatter(
                    y=[row["Site"], row["Site"]], x=[row["LCOE_Min"], row["LCOE_Max"]],
                    mode='lines+markers', line=dict(color="#10B981", width=6),
                    marker=dict(symbol="line-ns", size=10, color="#064E3B", line=dict(width=2, color="#064E3B")),
                    showlegend=False
                ))
            fig.update_layout(
                barmode='overlay', height=max(300, len(economics_df)*40), margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(title="USD per kWh", range=[0, max(economics_df["Avoided Cost"].max() + 0.1, 0.6)]), yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No economic data matches the selected connection type.")

    with c_metrics:
        st.markdown("**Deal Economics**")
        if not economics_df.empty:
            for idx, row in economics_df.iterrows():
                st.markdown(f"<div style='margin-bottom: 15px;'><b>{row['Site']}</b><br><span style='font-size:0.85rem; color:#4B5563;'>Payback: {row['Payback']} | Lease: {row['Lease_Comparison']}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Sector Heatmap")
    
    def color_heatmap(val):
        if 'Priority' in str(val): return 'background-color: #047857; color: white;'
        if 'Secondary' in str(val): return 'background-color: #D1FAE5; color: #064E3B;'
        if 'margin' in str(val) or 'Needs' in str(val) or 'Cash' in str(val): return 'background-color: #FEE2E2; color: #991B1B;'
        return ''
        
    filtered_heatmap = heatmap_df if selected_sector == "All" else heatmap_df[heatmap_df[selected_sector].isin(["Priority", "Priority - verify data", "Secondary"])]
    st.dataframe(filtered_heatmap.style.map(color_heatmap), use_container_width=True, hide_index=True)