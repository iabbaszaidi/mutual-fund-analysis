# 📊 Pakistan Mutual Fund Performance Analysis (2020–2024)

> **End-to-end data analytics project** covering NAV performance, AUM trends, risk-adjusted returns, benchmark comparison, and investor behaviour for Pakistan's mutual fund industry — built with Python, PostgreSQL, and Power BI.

---

## 🎯 Project Overview

This project analyses the performance of **6 Shariah-compliant mutual funds** over a 5-year period (2020–2024), modelled on Pakistan's Asset Management Company (AMC) industry. It covers the full analytics pipeline: data generation → SQL analysis → Python EDA → Power BI dashboards.

**Why this matters:** Pakistan's mutual fund industry has grown significantly in recent years. This project demonstrates how data analytics can help investment firms track fund performance, understand investor behaviour, and make data-driven strategic decisions.

---

## 🗂️ Project Structure

```
mutual_fund_analysis/
│
├── data/
│   ├── generate_data.py            # Synthetic dataset generator
│   ├── nav_history.csv             # 7,830 daily NAV records
│   ├── aum_history.csv             # 360 monthly AUM records
│   ├── investor_transactions.csv   # 4,200+ investor transactions
│   ├── kse100_benchmark.csv        # KSE-100 index proxy
│   └── powerbi_*.csv               # 5 pre-processed Power BI tables
│
├── notebooks/
│   └── analysis.py                 # Full Python EDA & analysis
│
├── sql/
│   └── analysis_queries.sql        # 10 production-ready SQL queries
│
├── powerbi/
│   └── POWERBI_SETUP.md            # Step-by-step dashboard guide + DAX
│
└── reports/
    ├── 01_nav_growth.png
    ├── 02_risk_return.png
    ├── 03_benchmark_comparison.png
    ├── 04_aum_trends.png
    └── 05_investor_analysis.png
```

---

## 📈 Key Findings

| Fund | Category | 5-Year CAGR | Sharpe Ratio |
|------|----------|-------------|--------------|
| Al Meezan Mutual Fund | Equity | **28.7%** | 0.58 |
| Meezan Islamic Income Fund | Income | 11.0% | — |
| Meezan Cash Fund | Money Market | 4.5% | — |
| Meezan Gold Fund | Commodity | 3.9% | — |
| KSE Meezan Index Fund | Index | — | — |
| Meezan Balanced Fund | Balanced | — | — |

**Highlights:**
- 🏆 **Al Meezan Mutual Fund** delivered the highest 5-year CAGR at ~28.7%
- 💧 **Meezan Cash Fund** had the lowest volatility — best for capital preservation
- 📉 COVID-19 (March–April 2020) caused a measurable drawdown in equity funds
- 🏙️ **Karachi** accounts for ~45% of all investor transactions
- 🏦 **Institutional investors** drive the highest average ticket size

---

## 🔍 Analysis Modules

### 1. NAV Growth & Returns
- Indexed NAV comparison (all funds vs base 100)
- 5-year total return & CAGR per fund
- Annual return breakdown (2020–2024)

### 2. Risk-Adjusted Performance
- Annualised volatility
- Sharpe Ratio (using 19% PKR risk-free rate proxy)
- Maximum Drawdown analysis
- Risk vs Return scatter

### 3. Benchmark Comparison
- Equity & Index funds vs KSE-100
- Alpha identification
- COVID-crash & recovery analysis

### 4. AUM Trend Analysis
- Total industry AUM growth (2020–2024)
- Category-wise AUM market share
- Year-over-year AUM growth rates

### 5. Investor Behaviour
- Net inflows/outflows by fund
- City-wise investment distribution
- Investor segmentation (Retail / HNI / Institutional)
- Retention rate proxy (repeat investors)

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.12** | Data generation, EDA, visualisation |
| **Pandas & NumPy** | Data manipulation & statistical analysis |
| **Matplotlib** | Chart generation |
| **PostgreSQL** | KPI queries, aggregations, views |
| **Power BI** | Interactive dashboards (4-page report) |

---

## 🚀 How to Run

### Python Analysis
```bash
# Clone the repo
git clone https://github.com/iabbaszaidi/mutual-fund-analysis.git
cd mutual-fund-analysis

# Install dependencies
pip install pandas numpy matplotlib

# Generate dataset
python data/generate_data.py

# Run full analysis
python notebooks/analysis.py
```

### SQL (PostgreSQL)
```bash
# Create database
createdb mutual_fund_db

# Load CSVs using COPY or pgAdmin
# Then run:
psql -d mutual_fund_db -f sql/analysis_queries.sql
```

### Power BI Dashboard
See [`powerbi/POWERBI_SETUP.md`](powerbi/POWERBI_SETUP.md) for full setup guide with DAX measures.

---

## 📊 Dashboard Preview

The Power BI report includes 4 pages:
1. **Executive Summary** — KPI cards, CAGR ranking, AUM donut
2. **NAV Performance** — Line charts, risk-return scatter, metrics table
3. **AUM & Inflows** — Area chart, stacked bar, net flow trends
4. **Investor Analytics** — City map, segment bar, investor table

---

## 👤 Author

**Mohammad Abbas**  
Data Analyst | Python · SQL · Power BI · Big Data  
📧 mohammadabbas456@outlook.com  
🔗 [LinkedIn](https://linkedin.com/in/mohammad-abbas-a23951248)  
💻 [GitHub](https://github.com/iabbaszaidi)

---

## 📝 Disclaimer

This project uses **synthetic data** generated programmatically, modelled on publicly observable patterns in Pakistan's AMC industry. It does not represent actual fund performance data. Created for educational and portfolio demonstration purposes.
