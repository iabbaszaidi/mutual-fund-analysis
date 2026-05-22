# %% [markdown]
# # 📊 Pakistan Mutual Fund Performance Analysis (2020–2024)
# **Tools:** Python · PostgreSQL · Power BI  
# **Author:** Mohammad Abbas  
# **Dataset:** Synthetic data modelled on Pakistan AMC industry  
#
# ---
# ## Objectives
# 1. Analyse NAV growth & risk-adjusted returns across fund categories
# 2. Benchmark equity/index funds against KSE-100
# 3. Segment investor behaviour by city, type, and fund preference
# 4. Identify AUM growth trends and top-performing funds
# 5. Build KPI outputs ready for Power BI dashboard

# %% Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "#F8FAFC",
    "axes.grid": True, "grid.alpha": 0.4, "font.family": "DejaVu Sans",
    "axes.spines.top": False, "axes.spines.right": False,
})
COLORS = ["#1B4F8C","#2E86C1","#85C1E9","#F39C12","#27AE60","#E74C3C"]

# %% Load Data
nav   = pd.read_csv("data/nav_history.csv",            parse_dates=["date"])
aum   = pd.read_csv("data/aum_history.csv",            parse_dates=["month"])
txn   = pd.read_csv("data/investor_transactions.csv",  parse_dates=["txn_date"])
bench = pd.read_csv("data/kse100_benchmark.csv",       parse_dates=["date"])

print("=== Dataset Overview ===")
print(f"NAV records       : {len(nav):,}  |  Funds: {nav['fund_id'].nunique()}")
print(f"AUM records       : {len(aum):,}  |  Months: {aum['month'].nunique()}")
print(f"Transactions      : {len(txn):,}  |  Investors: {txn['investor_id'].nunique()}")
print(f"Benchmark records : {len(bench):,}")
print(f"Date range        : {nav['date'].min().date()} → {nav['date'].max().date()}")

# %% ── 1. NAV GROWTH ANALYSIS ──────────────────────────────────────────────
print("\n=== 1. NAV Growth (2020–2024) ===")

# Yearly returns per fund
nav["year"] = nav["date"].dt.year
yearly_nav = (nav.groupby(["fund_id","fund_name","category","year"])
                  .agg(start_nav=("nav","first"), end_nav=("nav","last"))
                  .reset_index())
yearly_nav["annual_return_pct"] = ((yearly_nav["end_nav"] / yearly_nav["start_nav"]) - 1) * 100

# Full period return (2020 → 2024)
period_nav = (nav.groupby(["fund_id","fund_name","category"])
                  .agg(nav_2020=("nav","first"), nav_2024=("nav","last"))
                  .reset_index())
period_nav["total_return_pct"] = ((period_nav["nav_2024"] / period_nav["nav_2020"]) - 1) * 100
period_nav["cagr_pct"] = ((period_nav["nav_2024"] / period_nav["nav_2020"]) ** (1/5) - 1) * 100

print(period_nav[["fund_name","category","total_return_pct","cagr_pct"]].to_string(index=False))

# Plot: NAV over time (normalised to 100)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

funds_list = nav["fund_id"].unique()
for i, fid in enumerate(funds_list):
    sub = nav[nav["fund_id"]==fid].copy()
    sub["nav_norm"] = sub["nav"] / sub["nav"].iloc[0] * 100
    fname = sub["fund_name"].iloc[0].replace("Meezan ","")
    axes[0].plot(sub["date"], sub["nav_norm"], label=fname, color=COLORS[i], linewidth=1.5)

axes[0].set_title("NAV Growth (Indexed to 100)", fontweight="bold")
axes[0].set_ylabel("Indexed NAV")
axes[0].legend(fontsize=7, loc="upper left")

# Plot: CAGR bar chart
period_nav_sorted = period_nav.sort_values("cagr_pct", ascending=True)
axes[1].barh(period_nav_sorted["fund_name"].str.replace("Meezan ",""), 
             period_nav_sorted["cagr_pct"],
             color=COLORS[:len(period_nav_sorted)])
axes[1].set_title("5-Year CAGR by Fund (%)", fontweight="bold")
axes[1].set_xlabel("CAGR %")
for bar, val in zip(axes[1].patches, period_nav_sorted["cagr_pct"]):
    axes[1].text(bar.get_width()+0.2, bar.get_y()+bar.get_height()/2,
                 f"{val:.1f}%", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("reports/01_nav_growth.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart saved: reports/01_nav_growth.png")

# %% ── 2. RISK-ADJUSTED RETURNS ────────────────────────────────────────────
print("\n=== 2. Risk-Adjusted Returns (Sharpe Ratio) ===")

# Daily returns
nav_pivot = nav.pivot(index="date", columns="fund_id", values="nav")
daily_ret = nav_pivot.pct_change().dropna()

# Annualised metrics
risk_free_daily = 0.19 / 252  # ~19% PKR risk-free proxy

metrics = []
for fid in daily_ret.columns:
    r = daily_ret[fid].dropna()
    ann_ret  = (1 + r.mean()) ** 252 - 1
    ann_vol  = r.std() * np.sqrt(252)
    sharpe   = (ann_ret - 0.19) / ann_vol if ann_vol > 0 else 0
    max_dd   = ((nav_pivot[fid] / nav_pivot[fid].cummax()) - 1).min() * 100
    fname    = nav[nav["fund_id"]==fid]["fund_name"].iloc[0]
    cat      = nav[nav["fund_id"]==fid]["category"].iloc[0]
    metrics.append({"fund_id":fid, "fund_name":fname, "category":cat,
                    "ann_return_pct": ann_ret*100, "ann_volatility_pct": ann_vol*100,
                    "sharpe_ratio": sharpe, "max_drawdown_pct": max_dd})

risk_df = pd.DataFrame(metrics)
print(risk_df[["fund_name","ann_return_pct","ann_volatility_pct","sharpe_ratio","max_drawdown_pct"]].to_string(index=False))

# Plot: Risk vs Return scatter
fig, ax = plt.subplots(figsize=(9, 6))
for i, row in risk_df.iterrows():
    ax.scatter(row["ann_volatility_pct"], row["ann_return_pct"], 
               s=200, color=COLORS[i], zorder=3)
    ax.annotate(row["fund_name"].replace("Meezan ",""),
                (row["ann_volatility_pct"], row["ann_return_pct"]),
                textcoords="offset points", xytext=(8,4), fontsize=8)
ax.set_xlabel("Annualised Volatility (%)")
ax.set_ylabel("Annualised Return (%)")
ax.set_title("Risk vs Return by Fund (2020–2024)", fontweight="bold")
plt.tight_layout()
plt.savefig("reports/02_risk_return.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart saved: reports/02_risk_return.png")

# %% ── 3. BENCHMARK COMPARISON ─────────────────────────────────────────────
print("\n=== 3. Equity vs KSE-100 Benchmark ===")

equity_ids = ["F001","F005"]  # Al Meezan MF + Index Fund
eq_nav = nav[nav["fund_id"].isin(equity_ids)].copy()

bench_norm = bench.copy()
bench_norm["kse_norm"] = bench_norm["kse100_index"] / bench_norm["kse100_index"].iloc[0] * 100

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(bench_norm["date"], bench_norm["kse_norm"], label="KSE-100 Benchmark",
        color="gray", linewidth=1.5, linestyle="--")
for i, fid in enumerate(equity_ids):
    sub = eq_nav[eq_nav["fund_id"]==fid].copy()
    sub["nav_norm"] = sub["nav"] / sub["nav"].iloc[0] * 100
    ax.plot(sub["date"], sub["nav_norm"], label=sub["fund_name"].iloc[0], 
            color=COLORS[i], linewidth=2)

ax.set_title("Equity Funds vs KSE-100 Benchmark (Indexed to 100)", fontweight="bold")
ax.set_ylabel("Indexed Value")
ax.legend()
plt.tight_layout()
plt.savefig("reports/03_benchmark_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart saved: reports/03_benchmark_comparison.png")

# %% ── 4. AUM TREND ANALYSIS ───────────────────────────────────────────────
print("\n=== 4. AUM Trend Analysis ===")

total_aum = aum.groupby("month")["aum_million_pkr"].sum().reset_index()
cat_aum   = aum.groupby(["month","category"])["aum_million_pkr"].sum().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].fill_between(total_aum["month"], total_aum["aum_million_pkr"], 
                     alpha=0.3, color=COLORS[0])
axes[0].plot(total_aum["month"], total_aum["aum_million_pkr"], color=COLORS[0], linewidth=2)
axes[0].set_title("Total AUM Over Time (PKR Million)", fontweight="bold")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1000:.0f}B"))
axes[0].set_ylabel("AUM (PKR Billion)")

for i, cat in enumerate(cat_aum["category"].unique()):
    sub = cat_aum[cat_aum["category"]==cat]
    axes[1].plot(sub["month"], sub["aum_million_pkr"], label=cat, 
                 color=COLORS[i], linewidth=1.8)
axes[1].set_title("AUM by Fund Category", fontweight="bold")
axes[1].legend(fontsize=8)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1000:.1f}B"))

plt.tight_layout()
plt.savefig("reports/04_aum_trends.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart saved: reports/04_aum_trends.png")

# Latest AUM snapshot
latest_aum = aum[aum["month"]==aum["month"].max()].copy()
latest_aum["aum_share_pct"] = latest_aum["aum_million_pkr"] / latest_aum["aum_million_pkr"].sum() * 100
print(latest_aum[["fund_name","aum_million_pkr","aum_share_pct"]].to_string(index=False))

# %% ── 5. INVESTOR BEHAVIOUR ANALYSIS ─────────────────────────────────────
print("\n=== 5. Investor Behaviour Analysis ===")

txn["year"] = txn["txn_date"].dt.year
txn["month"]= txn["txn_date"].dt.to_period("M")

# Net inflows by fund
buys  = txn[txn["txn_type"]=="Buy"].groupby("fund_id")["amount_pkr"].sum()
sells = txn[txn["txn_type"]=="Sell"].groupby("fund_id")["amount_pkr"].sum()
inflow_df = pd.DataFrame({"gross_buy":buys,"gross_sell":sells}).fillna(0)
inflow_df["net_inflow"] = inflow_df["gross_buy"] - inflow_df["gross_sell"]
inflow_df = inflow_df.merge(nav[["fund_id","fund_name"]].drop_duplicates(), on="fund_id")
print("\nNet Inflows by Fund (PKR):")
print(inflow_df[["fund_name","gross_buy","gross_sell","net_inflow"]].to_string(index=False))

# City-wise investment
city_seg = txn[txn["txn_type"]=="Buy"].groupby(["city","investor_segment"])["amount_pkr"].sum().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

city_total = city_seg.groupby("city")["amount_pkr"].sum().sort_values(ascending=False)
axes[0].bar(city_total.index, city_total.values / 1e6, color=COLORS)
axes[0].set_title("Total Investment by City (PKR Million)", fontweight="bold")
axes[0].set_ylabel("PKR Million")
axes[0].tick_params(axis="x", rotation=30)

seg_total = txn[txn["txn_type"]=="Buy"].groupby("investor_segment")["amount_pkr"].sum()
axes[1].pie(seg_total.values, labels=seg_total.index, autopct="%1.1f%%",
            colors=COLORS[:3], startangle=90)
axes[1].set_title("Investment by Investor Segment", fontweight="bold")

plt.tight_layout()
plt.savefig("reports/05_investor_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("Chart saved: reports/05_investor_analysis.png")

# %% ── 6. EXPORT KPIs for Power BI ────────────────────────────────────────
print("\n=== 6. Exporting KPI Tables for Power BI ===")

# Table 1: Fund Master
fund_master = nav[["fund_id","fund_name","category","shariah_compliant"]].drop_duplicates()
fund_master = fund_master.merge(period_nav[["fund_id","total_return_pct","cagr_pct"]], on="fund_id")
fund_master = fund_master.merge(risk_df[["fund_id","ann_volatility_pct","sharpe_ratio","max_drawdown_pct"]], on="fund_id")
fund_master.to_csv("data/powerbi_fund_master.csv", index=False)

# Table 2: Monthly NAV (sampled last day of month)
nav_monthly = nav.copy()
nav_monthly["month"] = nav_monthly["date"].dt.to_period("M")
nav_monthly_last = nav_monthly.loc[nav_monthly.groupby(["fund_id","month"])["date"].idxmax()]
nav_monthly_last.to_csv("data/powerbi_nav_monthly.csv", index=False)

# Table 3: AUM
aum.to_csv("data/powerbi_aum.csv", index=False)

# Table 4: Investor Summary
investor_summary = (txn.groupby(["investor_id","city","investor_segment"])
                       .agg(total_invested=("amount_pkr","sum"),
                            num_transactions=("txn_id","count"),
                            funds_invested=("fund_id","nunique"))
                       .reset_index())
investor_summary.to_csv("data/powerbi_investor_summary.csv", index=False)

# Table 5: Monthly Net Inflows
monthly_inflow = (txn.groupby(["month","fund_id","fund_name","txn_type"])["amount_pkr"]
                     .sum().reset_index())
monthly_inflow["month"] = monthly_inflow["month"].astype(str)
monthly_inflow.to_csv("data/powerbi_monthly_inflows.csv", index=False)

print("Power BI tables exported:")
print("  ✓ powerbi_fund_master.csv")
print("  ✓ powerbi_nav_monthly.csv")
print("  ✓ powerbi_aum.csv")
print("  ✓ powerbi_investor_summary.csv")
print("  ✓ powerbi_monthly_inflows.csv")

print("\n✅ Full analysis complete! Check reports/ folder for charts.")
