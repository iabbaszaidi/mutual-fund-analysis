-- =============================================================
--  Pakistan Mutual Fund Performance Analysis – SQL Queries
--  Author  : Mohammad Abbas
--  Tools   : PostgreSQL
--  Purpose : KPI extraction, trend analysis, investor behaviour
-- =============================================================

-- ── TABLE SETUP ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fund_master (
    fund_id             VARCHAR(10) PRIMARY KEY,
    fund_name           VARCHAR(100),
    category            VARCHAR(50),
    shariah_compliant   BOOLEAN,
    total_return_pct    NUMERIC(8,4),
    cagr_pct            NUMERIC(8,4),
    ann_volatility_pct  NUMERIC(8,4),
    sharpe_ratio        NUMERIC(8,4),
    max_drawdown_pct    NUMERIC(8,4)
);

CREATE TABLE IF NOT EXISTS nav_history (
    date                DATE,
    fund_id             VARCHAR(10) REFERENCES fund_master(fund_id),
    fund_name           VARCHAR(100),
    category            VARCHAR(50),
    shariah_compliant   BOOLEAN,
    nav                 NUMERIC(12,4),
    PRIMARY KEY (date, fund_id)
);

CREATE TABLE IF NOT EXISTS aum_history (
    month               DATE,
    fund_id             VARCHAR(10) REFERENCES fund_master(fund_id),
    fund_name           VARCHAR(100),
    category            VARCHAR(50),
    aum_million_pkr     NUMERIC(14,2),
    PRIMARY KEY (month, fund_id)
);

CREATE TABLE IF NOT EXISTS investor_transactions (
    txn_id              VARCHAR(15) PRIMARY KEY,
    investor_id         VARCHAR(15),
    city                VARCHAR(50),
    investor_segment    VARCHAR(30),
    fund_id             VARCHAR(10) REFERENCES fund_master(fund_id),
    fund_name           VARCHAR(100),
    category            VARCHAR(50),
    txn_date            DATE,
    txn_type            VARCHAR(30),
    amount_pkr          NUMERIC(18,2)
);


-- ── QUERY 1: Fund Performance Scorecard ──────────────────────────────────
-- Ranks all funds by CAGR with risk context
SELECT
    fund_name,
    category,
    CASE WHEN shariah_compliant THEN 'Shariah' ELSE 'Conventional' END AS compliance,
    ROUND(cagr_pct, 2)            AS cagr_pct,
    ROUND(total_return_pct, 2)    AS total_5yr_return_pct,
    ROUND(ann_volatility_pct, 2)  AS volatility_pct,
    ROUND(sharpe_ratio, 3)        AS sharpe_ratio,
    ROUND(max_drawdown_pct, 2)    AS max_drawdown_pct,
    RANK() OVER (ORDER BY cagr_pct DESC) AS performance_rank
FROM fund_master
ORDER BY cagr_pct DESC;


-- ── QUERY 2: Monthly NAV Change % ────────────────────────────────────────
-- Rolling month-over-month NAV change for trend tracking
WITH monthly_nav AS (
    SELECT
        DATE_TRUNC('month', date)::DATE AS month,
        fund_id,
        fund_name,
        category,
        LAST_VALUE(nav) OVER (
            PARTITION BY fund_id, DATE_TRUNC('month', date)
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS month_end_nav
    FROM nav_history
),
distinct_monthly AS (
    SELECT DISTINCT month, fund_id, fund_name, category, month_end_nav
    FROM monthly_nav
)
SELECT
    month,
    fund_name,
    category,
    ROUND(month_end_nav, 4) AS nav,
    ROUND(
        (month_end_nav - LAG(month_end_nav) OVER (PARTITION BY fund_id ORDER BY month))
        / NULLIF(LAG(month_end_nav) OVER (PARTITION BY fund_id ORDER BY month), 0) * 100,
    2) AS mom_return_pct
FROM distinct_monthly
ORDER BY fund_id, month;


-- ── QUERY 3: AUM Market Share by Category ────────────────────────────────
-- Latest month AUM breakdown
WITH latest AS (
    SELECT MAX(month) AS max_month FROM aum_history
)
SELECT
    a.category,
    ROUND(SUM(a.aum_million_pkr), 2)                              AS aum_million_pkr,
    ROUND(SUM(a.aum_million_pkr) / SUM(SUM(a.aum_million_pkr)) OVER () * 100, 2) AS market_share_pct
FROM aum_history a
JOIN latest l ON a.month = l.max_month
GROUP BY a.category
ORDER BY aum_million_pkr DESC;


-- ── QUERY 4: AUM Growth Rate Year-over-Year ──────────────────────────────
WITH yearly_aum AS (
    SELECT
        EXTRACT(YEAR FROM month)::INT AS year,
        fund_id,
        fund_name,
        SUM(aum_million_pkr) / 12 AS avg_annual_aum
    FROM aum_history
    GROUP BY year, fund_id, fund_name
)
SELECT
    y.year,
    y.fund_name,
    ROUND(y.avg_annual_aum, 2) AS avg_aum,
    ROUND(
        (y.avg_annual_aum - LAG(y.avg_annual_aum) OVER (PARTITION BY y.fund_id ORDER BY y.year))
        / NULLIF(LAG(y.avg_annual_aum) OVER (PARTITION BY y.fund_id ORDER BY y.year), 0) * 100,
    2) AS yoy_growth_pct
FROM yearly_aum y
ORDER BY fund_name, year;


-- ── QUERY 5: Net Investor Inflows by Fund ────────────────────────────────
SELECT
    fund_name,
    category,
    ROUND(SUM(CASE WHEN txn_type = 'Buy'  THEN amount_pkr ELSE 0 END) / 1e6, 2) AS gross_buy_mn,
    ROUND(SUM(CASE WHEN txn_type = 'Sell' THEN amount_pkr ELSE 0 END) / 1e6, 2) AS gross_sell_mn,
    ROUND(SUM(CASE WHEN txn_type = 'Buy'  THEN amount_pkr
                   WHEN txn_type = 'Sell' THEN -amount_pkr ELSE 0 END) / 1e6, 2) AS net_inflow_mn
FROM investor_transactions
GROUP BY fund_name, category
ORDER BY net_inflow_mn DESC;


-- ── QUERY 6: Investor Acquisition & Behaviour by City ────────────────────
SELECT
    city,
    investor_segment,
    COUNT(DISTINCT investor_id)                                     AS total_investors,
    COUNT(txn_id)                                                   AS total_transactions,
    ROUND(SUM(CASE WHEN txn_type = 'Buy' THEN amount_pkr END)/1e6, 2) AS total_invested_mn,
    ROUND(AVG(CASE WHEN txn_type = 'Buy' THEN amount_pkr END)/1e3, 2) AS avg_ticket_size_k
FROM investor_transactions
GROUP BY city, investor_segment
ORDER BY total_invested_mn DESC;


-- ── QUERY 7: Top 10 Investors by Portfolio Size ──────────────────────────
SELECT
    investor_id,
    city,
    investor_segment,
    COUNT(DISTINCT fund_id)                                         AS funds_in_portfolio,
    COUNT(txn_id)                                                   AS total_transactions,
    ROUND(SUM(CASE WHEN txn_type = 'Buy'  THEN amount_pkr ELSE 0 END) / 1e6, 2) AS total_invested_mn,
    ROUND(SUM(CASE WHEN txn_type = 'Sell' THEN amount_pkr ELSE 0 END) / 1e6, 2) AS total_redeemed_mn
FROM investor_transactions
GROUP BY investor_id, city, investor_segment
ORDER BY total_invested_mn DESC
LIMIT 10;


-- ── QUERY 8: Monthly Inflow Trend (for Power BI line chart) ──────────────
SELECT
    DATE_TRUNC('month', txn_date)::DATE AS month,
    fund_name,
    category,
    ROUND(SUM(CASE WHEN txn_type = 'Buy'  THEN amount_pkr ELSE 0 END) / 1e6, 2) AS inflow_mn,
    ROUND(SUM(CASE WHEN txn_type = 'Sell' THEN amount_pkr ELSE 0 END) / 1e6, 2) AS outflow_mn,
    ROUND(SUM(CASE WHEN txn_type IN ('Buy','Sell')
                   THEN (CASE WHEN txn_type='Buy' THEN amount_pkr ELSE -amount_pkr END)
                   ELSE 0 END) / 1e6, 2) AS net_flow_mn
FROM investor_transactions
GROUP BY month, fund_name, category
ORDER BY month, fund_name;


-- ── QUERY 9: Retention Proxy – Repeat Investors per Fund ────────────────
SELECT
    fund_name,
    category,
    COUNT(DISTINCT investor_id)                             AS unique_investors,
    COUNT(DISTINCT CASE WHEN txn_count > 1
        THEN investor_id END)                               AS repeat_investors,
    ROUND(COUNT(DISTINCT CASE WHEN txn_count > 1
        THEN investor_id END)::NUMERIC
        / NULLIF(COUNT(DISTINCT investor_id),0) * 100, 1)  AS retention_rate_pct
FROM (
    SELECT investor_id, fund_id, fund_name, category,
           COUNT(txn_id) AS txn_count
    FROM investor_transactions
    WHERE txn_type = 'Buy'
    GROUP BY investor_id, fund_id, fund_name, category
) sub
GROUP BY fund_name, category
ORDER BY retention_rate_pct DESC;


-- ── QUERY 10: KPI Summary Dashboard View ─────────────────────────────────
CREATE OR REPLACE VIEW vw_kpi_summary AS
SELECT
    fm.fund_name,
    fm.category,
    fm.shariah_compliant,
    ROUND(fm.cagr_pct, 2)                   AS cagr_5yr_pct,
    ROUND(fm.sharpe_ratio, 3)               AS sharpe_ratio,
    ROUND(fm.max_drawdown_pct, 2)           AS max_drawdown_pct,
    ROUND(latest_aum.aum_million_pkr, 2)    AS latest_aum_mn,
    ROUND(net_flows.net_inflow_mn, 2)       AS net_inflow_mn,
    ROUND(investors.unique_investors, 0)    AS unique_investors
FROM fund_master fm
LEFT JOIN (
    SELECT fund_id, aum_million_pkr
    FROM aum_history
    WHERE month = (SELECT MAX(month) FROM aum_history)
) latest_aum USING (fund_id)
LEFT JOIN (
    SELECT fund_id,
           SUM(CASE WHEN txn_type='Buy'  THEN amount_pkr
                    WHEN txn_type='Sell' THEN -amount_pkr ELSE 0 END)/1e6 AS net_inflow_mn
    FROM investor_transactions
    GROUP BY fund_id
) net_flows USING (fund_id)
LEFT JOIN (
    SELECT fund_id, COUNT(DISTINCT investor_id) AS unique_investors
    FROM investor_transactions
    GROUP BY fund_id
) investors USING (fund_id)
ORDER BY cagr_5yr_pct DESC;

SELECT * FROM vw_kpi_summary;
