"""
Dataset Generator – Pakistan Mutual Fund Performance Dataset
Generates realistic synthetic data inspired by Pakistani AMC industry (2020–2024)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ── Fund Definitions ────────────────────────────────────────────────────────
funds = [
    {"fund_id": "F001", "name": "Al Meezan Mutual Fund",        "category": "Equity",       "shariah": True,  "inception": "2005-01-01", "base_nav": 85.0,  "aum_base": 12000},
    {"fund_id": "F002", "name": "Meezan Islamic Income Fund",   "category": "Income",       "shariah": True,  "inception": "2007-06-01", "base_nav": 12.5,  "aum_base": 8500},
    {"fund_id": "F003", "name": "Meezan Cash Fund",             "category": "Money Market", "shariah": True,  "inception": "2010-03-01", "base_nav": 10.2,  "aum_base": 18000},
    {"fund_id": "F004", "name": "Meezan Balanced Fund",         "category": "Balanced",     "shariah": True,  "inception": "2012-09-01", "base_nav": 22.0,  "aum_base": 5000},
    {"fund_id": "F005", "name": "KSE Meezan Index Fund",        "category": "Index",        "shariah": True,  "inception": "2015-01-01", "base_nav": 45.0,  "aum_base": 3200},
    {"fund_id": "F006", "name": "Meezan Gold Fund",             "category": "Commodity",    "shariah": True,  "inception": "2018-04-01", "base_nav": 18.0,  "aum_base": 2100},
]

# ── NAV History ─────────────────────────────────────────────────────────────
start_date = datetime(2020, 1, 1)
end_date   = datetime(2024, 12, 31)
dates = pd.date_range(start_date, end_date, freq="B")  # business days

volatility_map = {"Equity": 0.012, "Income": 0.002, "Money Market": 0.0008,
                  "Balanced": 0.006, "Index": 0.013, "Commodity": 0.010}
drift_map      = {"Equity": 0.00045, "Income": 0.00025, "Money Market": 0.00018,
                  "Balanced": 0.00030, "Index": 0.00042, "Commodity": 0.00035}

nav_rows = []
for f in funds:
    nav = f["base_nav"]
    vol  = volatility_map[f["category"]]
    drift= drift_map[f["category"]]
    for dt in dates:
        shock = 0
        # COVID crash Mar 2020
        if datetime(2020,3,1) <= dt <= datetime(2020,4,30) and f["category"] in ["Equity","Index","Balanced"]:
            shock = -0.008
        # Recovery 2020-2021
        if datetime(2020,7,1) <= dt <= datetime(2021,6,30) and f["category"] in ["Equity","Index"]:
            shock = 0.002
        # Inflation/rate hike pressure 2022
        if datetime(2022,1,1) <= dt <= datetime(2022,12,31) and f["category"] == "Income":
            shock = 0.0005
        daily_return = drift + shock + np.random.normal(0, vol)
        nav = nav * (1 + daily_return)
        nav = max(nav, 1.0)
        nav_rows.append({
            "date": dt.date(),
            "fund_id": f["fund_id"],
            "fund_name": f["name"],
            "category": f["category"],
            "shariah_compliant": f["shariah"],
            "nav": round(nav, 4),
        })

nav_df = pd.DataFrame(nav_rows)

# ── AUM History (monthly) ────────────────────────────────────────────────────
months = pd.date_range("2020-01-01", "2024-12-01", freq="MS")
aum_rows = []
for f in funds:
    aum = f["aum_base"]
    for m in months:
        growth = np.random.normal(0.01, 0.03)
        # industry boom 2021-22
        if datetime(2021,1,1) <= m.to_pydatetime() <= datetime(2022,6,30):
            growth += 0.015
        aum = max(aum * (1 + growth), 500)
        aum_rows.append({
            "month": m.date(),
            "fund_id": f["fund_id"],
            "fund_name": f["name"],
            "category": f["category"],
            "aum_million_pkr": round(aum, 2),
        })
aum_df = pd.DataFrame(aum_rows)

# ── Investor Transactions ────────────────────────────────────────────────────
investor_ids = [f"INV{str(i).zfill(4)}" for i in range(1, 501)]
cities = ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Peshawar", "Quetta"]
city_weights = [0.45, 0.28, 0.15, 0.06, 0.04, 0.02]
seg_map = {"Retail": 0.60, "HNI": 0.25, "Institutional": 0.15}

txn_rows = []
txn_id = 1
for inv in investor_ids:
    city = random.choices(cities, weights=city_weights)[0]
    segment = random.choices(list(seg_map.keys()), weights=list(seg_map.values()))[0]
    n_txn = random.randint(2, 15)
    for _ in range(n_txn):
        fund = random.choice(funds)
        dt = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        txn_type = random.choices(["Buy", "Sell", "Dividend Reinvest"], weights=[0.60, 0.28, 0.12])[0]
        base_amt = {"Retail": 50000, "HNI": 500000, "Institutional": 5000000}[segment]
        amount = round(random.uniform(0.5, 3.0) * base_amt, 2)
        txn_rows.append({
            "txn_id": f"TXN{str(txn_id).zfill(6)}",
            "investor_id": inv,
            "city": city,
            "investor_segment": segment,
            "fund_id": fund["fund_id"],
            "fund_name": fund["name"],
            "category": fund["category"],
            "txn_date": dt.date(),
            "txn_type": txn_type,
            "amount_pkr": amount,
        })
        txn_id += 1

txn_df = pd.DataFrame(txn_rows).sort_values("txn_date").reset_index(drop=True)

# ── Benchmark Returns (KSE-100 proxy) ───────────────────────────────────────
bench_rows = []
bench_val = 35000
for dt in dates:
    bench_val = bench_val * (1 + np.random.normal(0.0004, 0.011))
    bench_rows.append({"date": dt.date(), "kse100_index": round(bench_val, 2)})
bench_df = pd.DataFrame(bench_rows)

# ── Save ─────────────────────────────────────────────────────────────────────
nav_df.to_csv("/home/claude/mutual_fund_analysis/data/nav_history.csv", index=False)
aum_df.to_csv("/home/claude/mutual_fund_analysis/data/aum_history.csv", index=False)
txn_df.to_csv("/home/claude/mutual_fund_analysis/data/investor_transactions.csv", index=False)
bench_df.to_csv("/home/claude/mutual_fund_analysis/data/kse100_benchmark.csv", index=False)

print(f"NAV rows:         {len(nav_df):,}")
print(f"AUM rows:         {len(aum_df):,}")
print(f"Transaction rows: {len(txn_df):,}")
print(f"Benchmark rows:   {len(bench_df):,}")
print("All datasets saved!")
