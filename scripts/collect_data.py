import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_sample_data():
    # 1. Scorecard Data (Raw 1-5 Scores)
    scorecard = pd.DataFrame({
        "MARKET": [
            "Chile", "Zambia", "Philippines", "South Africa", "Saudi Arabia / UAE", 
            "Peru", "Mexico", "Kenya", "Nigeria", "Indonesia", "DRC (Copperbelt)",
            "Dominican Republic", "Bahamas", "Greece", "Spain"
        ],
        "OFFTAKERS":     [4, 4, 4, 5, 5, 4, 5, 4, 5, 4, 4, 4, 3, 5, 5],
        "ECONOMICS":     [3, 5, 4.5, 2.5, 2.5, 4, 3, 4, 5, 3, 5, 4.5, 5, 2, 2],
        "RECURRING_FIT": [5, 4, 4, 5, 4, 4, 4, 3.5, 3, 3, 2, 4, 4, 5, 5],
        "CURRENCY":      [4.5, 2, 4, 3, 5, 4, 3.5, 4, 2, 3.5, 4, 3.5, 4, 5, 5],
        "REGULATION":    [4.5, 4, 3.5, 4, 3, 3, 3, 3, 2.5, 2.5, 2, 3.5, 3.5, 4.5, 4.5],
        "FINANCE":       [4.5, 3, 4, 3.5, 4, 3.5, 4, 4, 3, 3.5, 2, 3, 3, 4.5, 4.5],
        "POLITICAL":     [4.5, 4, 3.5, 3.5, 1.5, 2.5, 3, 3, 2, 3.5, 1.5, 3, 3.5, 4, 4.5],
        "RIGHT_TO_WIN":  [2, 4, 2.5, 1, 2, 3, 1.5, 2, 2, 2.5, 3, 2, 2, 1, 1],
        "LEAD MODEL": [
            "B rental", "A - B - C", "A + C", "B fleet", "B", 
            "B rental", "A", "A + lease", "A", "A + B", "A prepaid",
            "A + lease", "A + lease", "C PPA", "C PPA"
        ]
    })

    # 2. Economics Data (Mapped to Connection Types)
    economics = pd.DataFrame({
        "Site": [
            "Peru off-grid camp", "Chile off-grid, Sep diesel", "Kenya lodge / estate, all diesel", 
            "Zambia all-diesel site", "Nigeria all-diesel factory", "Dominican Republic off-grid resort",
            "Kenya 60% grid / 40% diesel", "South Africa 70% grid / 30% diesel", "Bahamas island grid",
            "Philippines island site", "Philippines 1 MWp rooftop - grid-tied", "South Africa 1 MWp rooftop - grid-tied",
            "Spain 1 MWp rooftop - grid-tied"
        ],
        "Connection": [
            "Off-grid", "Off-grid", "Off-grid", 
            "Off-grid", "Off-grid", "Off-grid",
            "Weak grid / hybrid", "Weak grid / hybrid", "Weak grid / hybrid",
            "Weak grid / hybrid", "Grid-tied", "Grid-tied",
            "Grid-tied"
        ],
        "Avoided Cost": [0.54, 0.50, 0.53, 0.46, 0.43, 0.48, 0.32, 0.27, 0.35, 0.30, 0.15, 0.13, 0.16],
        "LCOE_Min": [0.18, 0.18, 0.22, 0.22, 0.21, 0.20, 0.16, 0.15, 0.18, 0.26, 0.10, 0.08, 0.07],
        "LCOE_Max": [0.28, 0.27, 0.33, 0.31, 0.30, 0.28, 0.22, 0.21, 0.25, 0.34, 0.13, 0.11, 0.10],
        "Payback": ["2.1 yrs", "2.0 yrs", "2.7 yrs", "2.8 yrs", "3.9 yrs", "2.6 yrs", "4.4 yrs", "4.1 yrs", "3.5 yrs", "5.6 yrs", "4.8 yrs", "4.5 yrs", "4.0 yrs"],
        "Lease_Comparison": ["50-54% cheaper", "53-57% cheaper", "36-42% cheaper", "33-39% cheaper", "9-17% cheaper", "40-45% cheaper", "1% dearer to 8% cheaper", "4-12% cheaper", "20-25% cheaper", "15-26% dearer", "PPA 0.110-0.127", "PPA 0.087-0.100", "PPA 0.080-0.095"]
    })

    # 3. Sector Heatmap Data
    heatmap = pd.DataFrame({
        "MARKET": [
            "Zambia", "Philippines", "South Africa", "Chile", "Peru", "Kenya", "Nigeria", 
            "Dominican Republic", "Bahamas", "Greece", "Spain"
        ],
        "Mining": [
            "Priority", "Secondary", "Secondary", "Priority", "Priority", "Not assessed", "Not assessed",
            "Not assessed", "Not assessed", "Not assessed", "Secondary"
        ],
        "Hospitality": [
            "Secondary", "Priority", "Not assessed", "Not assessed", "Not assessed", "Priority - verify data", "Not assessed",
            "Priority", "Priority", "Priority", "Priority"
        ],
        "Agro-Export": [
            "Secondary", "Secondary", "Secondary", "Not assessed", "Secondary", "Priority", "Not assessed",
            "Secondary", "Not assessed", "Secondary", "Priority"
        ],
        "Grid-tied C&I": [
            "Secondary", "Priority", "Low margin", "Low margin", "Not assessed", "Low margin", "Cash sales only",
            "Secondary", "Not assessed", "Low margin", "Low margin"
        ]
    })

    scorecard.to_parquet(DATA_DIR / "scorecard.parquet", index=False)
    economics.to_parquet(DATA_DIR / "economics.parquet", index=False)
    heatmap.to_parquet(DATA_DIR / "heatmap.parquet", index=False)
    print(f"Sample data generated successfully in {DATA_DIR}")

if __name__ == "__main__":
    generate_sample_data()