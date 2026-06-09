# Code Logic — Macro App

This document maps each section of `dashboard.py` to the corresponding logic in `macro-logic.md`.

---

## Architecture

`dashboard.py` is a single-page Streamlit app with 9 sections, each rendered as a horizontal row of fixed-width (160px) metric cards. Data fetched via `yfinance`, `requests`, and FRED CSV API, refreshing every 30 seconds via `st.rerun()`.

### Key functions

| Function | Purpose |
|----------|---------|
| `fmt_delta(delta, pct)` | Shared delta string formatter. Handles None safely. Returns `+1.2 (+0.5%)` style string or just `+1.2` if pct unavailable. |
| `fetch(ticker)` | yfinance `fast_info` — last price, previous close, delta, % change |
| `fetch_ratio(t1, t2)` | Fetches ratio of two tickers (e.g. HYG/TLT, RSP/SPY) with delta vs previous close ratio |
| `_parse_fred_csv(text)` | Shared FRED CSV parser. Handles `\r\n` and `\r` line endings, skips header and empty/`.` values. Returns list of `(date, float)` tuples, newest last. |
| `fetch_fred(series_id, cache_key)` | Latest single value + date. Uses `_parse_fred_csv`. Cached 1hr. |
| `fetch_fred_yoy(series_id, cache_key)` | YoY % change: `obs[-1]` vs `obs[-13]`. Used for CPI. Returns `(value, yoy_pct, date)`. Cached 1hr. |
| `fetch_fred_mom(series_id, cache_key)` | Month-on-month change: `obs[-1]` minus `obs[-2]`. Used for NFP. Returns `(value, mom, date)`. Cached 1hr. |
| `fetch_put_call()` | CNN F&G API `put_and_call_options.score`. No previous_close in sub-component — delta tracked via `session_state['pc_prev']`, n/a on first load. |
| `fetch_fear_greed_cnn()` | CNN F&G composite score + rating + delta from `fear_and_greed.previous_close` |
| `fetch_fear_greed_crypto()` | alternative.me crypto F&G, `?limit=2` for today + yesterday delta |
| `shorten_rating(rating)` | Abbreviates long ratings (Extreme Fear → Ext Fear) to prevent truncation in 160px columns |
| `show_metric(col, label, ticker, help_text)` | Standard metric card with delta, % change, tooltip |

---

## Sections

### 1. Risk Sentiment
**Logic ref:** `macro-logic.md` → Inputs → Price/Market, Classification Logic context layer

| Label | Ticker/Source | Type | Notes |
|-------|--------------|------|-------|
| VIX | ^VIX | Spot | Fear gauge. Spot used — VIX futures behave differently |
| DXY | DX-Y.NYB | Spot/cash | Dollar index. `DX=F` futures preferred but unavailable on yfinance. Small discrepancy vs Finviz. |
| Put/Call | CNN F&G API `put_and_call_options.score` | Derived | CNN-normalised CBOE ratio 0-100. Delta via session_state. |
| F&G Stocks | production.dataviz.cnn.io | Composite | CNN equity Fear & Greed. Delta from `previous_close`. Rating abbreviated if delta unavailable. |

**F&G Stocks — 7 sub-indicators:**
1. Market momentum (S&P vs 125-day MA)
2. Stock price strength (52-week highs vs lows on NYSE)
3. Stock price breadth (advancing vs declining volume)
4. Put/Call options (CBOE ratio)
5. Junk bond demand (spread between high-yield and investment-grade)
6. Market volatility (VIX vs 50-day MA)
7. Safe haven demand (stock vs bond returns)

Contrarian signal at extremes: below 25 = long-term value buyers historically step in. Above 75 = market most vulnerable to pullback.

**Put/Call sourcing history:** CBOE scraping blocked (403). yfinance tickers ^PCCR, ^CPC, ^CPCE all return empty. CNN F&G `put_and_call_options` top-level key is the only working free source.

---

### 2. Equity Futures & Indices
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

US indices use futures (24/7, captures overnight risk). International use cash (stale when markets closed).

| Label | Ticker | Type |
|-------|--------|------|
| S&P 500 | ES=F | Futures |
| NASDAQ | NQ=F | Futures |
| Nikkei | ^N225 | Cash |
| EuroStoxx | ^STOXX50E | Cash |
| DAX | ^GDAXI | Cash |
| KOSPI | ^KS11 | Cash |
| CSI 300 | 000300.SS | Cash |

---

### 3. Rates
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

All spot yields. Spread (10-2yr) is a calculated field — both yields fetched, previous closes fetched separately for spread delta.

| Label | Ticker | Purpose |
|-------|--------|---------|
| 2yr Yield | ^IRX | Fed expectations proxy |
| 5yr Yield | ^FVX | Mid-curve |
| 10yr Yield | ^TNX | Global benchmark rate |
| 30yr Yield | ^TYX | Long-end inflation expectations |
| Spread (10-2yr) | calculated | Negative = inverted = recession signal. Delta = narrowing (flattening) vs widening (steepening). |

---

### 4. Stress & Credit
**Logic ref:** `macro-logic.md` → Classification Logic — macro catalyst present overnight

| Label | Ticker/Source | Reference levels |
|-------|--------------|-----------------|
| MOVE Index | ^MOVE | Normal <80. Elevated 80–100. Stress 100–150. Crisis >150. (COVID peak ~160, 2023 banking crisis ~140) |
| HYG | HYG | Normal $76–$82. Stress $70–$76. Crisis <$70. (COVID low ~$68, 2022 low ~$70) |
| JNK | JNK | Normal $92–$100. Stress $85–$92. Crisis <$85. Confirms HYG. |
| HYG/TLT | fetch_ratio("HYG","TLT") | Direction matters more than level. Sustained decline = credit warning ahead of equities. |
| TLT | TLT | Inverse of long rates. TLT up + equities down = risk-off. TLT down + equities up = reflation. |

**Why this row matters:** Bond and credit markets price risk before equities. MOVE and HYG/TLT divergences from equity indices are early warning signals for the rebalancing vs reversal classification.

---

### 5. Breadth
**Logic ref:** `macro-logic.md` → Classification Logic — is today's move structural or narrow?

| Label | Ticker/Source | Notes |
|-------|--------------|-------|
| RSP | RSP | Equal-weight S&P 500 ETF |
| SPY | SPY | Market-cap weighted S&P 500 ETF |
| RSP/SPY | fetch_ratio("RSP","SPY") | Breadth indicator. Rising = broad participation. Falling = mega-cap driven, fragile rally. |

**How to read RSP/SPY:** If SPY is up but RSP/SPY is falling, the index gain is driven by a handful of large-cap names. The underlying market is weakening. Used as a structural confirmation input for sector flow analysis later.

---

### 6. Macro Data
**Logic ref:** `macro-logic.md` → Inputs → Macro Data (FRED API)

All FRED data uses the free CSV endpoint (`fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES`). No API key required. Cached in session_state for 1 hour.

| Label | Source | Frequency | Reference levels |
|-------|--------|-----------|-----------------|
| Fed Funds Implied | ZQ=F (yfinance) | Live | Compare to current FOMC target. Gap = market pricing cuts/hikes. Overnight shift = catalyst changed rate expectations. |
| Jobless Claims | FRED: ICSA | Weekly (Thu 8:30am ET) | Healthy <220k. Normal 220–260k. Elevated 260–300k. Concern 300–400k. Recession signal >400k sustained. (2020 peak: 6.1M) |
| CPI YoY | FRED: CPIAUCSL | Monthly | YoY % calculated via `fetch_fred_yoy()` — fetches full history, computes current vs 12 months prior. Fed target ~2%. Cooling 2–3%. Hot 3–5%. Crisis >6% (2022 peak 9.1%). |
| NFP MoM | FRED: PAYEMS | Monthly (first Fri) | `fetch_fred_mom()` — current minus previous obs. Shows monthly job adds directly. Strong >+250k. Healthy +150–250k. Weak <+50k. Recession = negative. |

**Display:** Value shown as main metric. Release date shown as delta label (grey, `delta_color="off"`). Future build: add next release date when FRED release calendar API is integrated.

---

### 7. Commodity Futures

| Label | Ticker | Purpose |
|-------|--------|---------|
| WTI Crude | CL=F | US oil benchmark + inflation signal |
| Brent Crude | BZ=F | Global benchmark |
| Gold | GC=F | Safe haven / inflation hedge / dollar inverse |
| Silver | SI=F | Industrial + safe haven hybrid |
| Copper | HG=F | Global growth leading indicator |

---

### 8. Crypto

| Label | Ticker/Source | Purpose |
|-------|--------------|---------|
| Bitcoin | BTC-USD | Risk-on/off signal + digital gold proxy |
| Ethereum | ETH-USD | Higher beta, DeFi/tech sentiment |
| F&G Crypto | api.alternative.me/fng/?limit=2 | Crypto sentiment only. Delta vs yesterday. Below 10 = capitulation. Above 80 = overheated. |

---

### 9. Currencies

| Label | Ticker | Purpose |
|-------|--------|---------|
| EUR/USD | EURUSD=X | Euro strength vs dollar |
| USD/JPY | JPY=X | Yen safe haven indicator |
| GBP/USD | GBPUSD=X | UK macro proxy |
| USD/CNY | USDCNY=X | Yuan strength — China stress |

---

## Open Items
- DXY: using spot `DX-Y.NYB` — small discrepancy vs Finviz (`DX=F`). Fix when alternative source found.
- International equity indices: cash prices go stale when markets are closed.
- FRED next release dates: `fetch_fred()` has placeholder for next_date — requires FRED API key for release calendar endpoint. Add when key available.
- Sector ETF flow row: planned next build. Will need `fetch_with_volume()` for price + volume vs 20-day avg.
- Events calendar: planned future build. Will consume `release_date` and `next_date` fields already structured in `fetch_fred()`.
- Jobless Claims: shows raw weekly number — MoM or 4-week moving average would add more signal. Future improvement.

## Refresh Rate
- **Current: 120 seconds (2 minutes).** Reduced from 30s — dashboard now has ~20 data sources, 30s caused excessive API load.
- FRED data is cached for 1hr in session_state, so refresh only re-fetches yfinance and CNN calls.
- If deploying to Streamlit Cloud, consider caching yfinance calls too (`@st.cache_data(ttl=120)`).
