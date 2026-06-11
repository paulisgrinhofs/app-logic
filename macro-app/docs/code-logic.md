# Code Logic — Macro App

This document maps each section of `dashboard.py` to the corresponding logic in `macro-logic.md`.

---

## Architecture

`dashboard.py` is a single-page Streamlit app with 9 sections, each rendered as a horizontal row of fixed-width (160px) metric cards. Data fetched via `yfinance`, `requests`, and FRED JSON API, refreshing every 120 seconds via `st.rerun()`.

### Key functions

| Function | Purpose |
|----------|---------|
| `fmt_delta(delta, pct)` | Shared delta string formatter. Handles None safely. Returns `+1.2 (+0.5%)` style string or just `+1.2` if pct unavailable. |
| `fetch(ticker)` | yfinance `fast_info` — last price, previous close, delta, % change |
| `fetch_ratio(t1, t2)` | Fetches ratio of two tickers (e.g. HYG/TLT, RSP/SPY) with delta vs previous close ratio |
| `_fetch_fred_raw(series_id)` | Fetches FRED observations via JSON API with API key. Returns list of `(date, float)` tuples, newest last. Cached 1hr. |
| `_prefetch_slow()` | Runs FRED fetches (ICSA, CPIAUCSL, PAYEMS) in parallel threads before page renders. Writes results to `session_state`. ZQ=F excluded — fetched inline instead (Streamlit blocks session_state writes from threads). |
| `fetch_fred(series_id, cache_key)` | Latest single value + date. Uses `_fetch_fred_raw`. Cached 1hr. |
| `fetch_fred_yoy(series_id, cache_key)` | YoY % change: `obs[-1]` vs `obs[-13]`. Used for CPI. Returns `(value, yoy_pct, date)`. Cached 1hr. |
| `fetch_fred_mom(series_id, cache_key)` | Month-on-month change: `obs[-1]` minus `obs[-2]`. Used for NFP. Returns `(value, mom, date)`. Cached 1hr. |
| `fetch_put_call()` | CNN F&G API `put_and_call_options.score`. Delta persisted to `.pc_prev.json` on disk — survives Streamlit restarts. Compares current score to last known value. |
| `_load_pc_prev()` | Reads previous Put/Call score from `macro-app/.pc_prev.json`. Returns score only if saved date is a previous calendar day. Returns None on first ever run. |
| `_save_pc_prev(score)` | Writes current score + today's date to `.pc_prev.json`. Will not overwrite if file already has today's date — reference point locked at first fetch of each day. File is committed to GitHub so it persists across machines and fresh clones. |
| `fetch_fear_greed_cnn()` | CNN F&G composite score + rating + delta from `fear_and_greed.previous_close` |
| `fetch_fear_greed_crypto()` | alternative.me crypto F&G, `?limit=2` for today + yesterday delta |
| `shorten_rating(rating)` | Abbreviates long ratings (Extreme Fear → Ext Fear) to prevent truncation in 160px columns |
| `show_metric(col, label, ticker, help_text)` | Standard metric card with delta, % change, tooltip |

---

## Sections

### 1. Risk Sentiment

| Label | Ticker/Source | Type | Notes |
|-------|--------------|------|-------|
| VIX | ^VIX | Spot | Fear gauge. Spot used — VIX futures behave differently |
| DXY | DX-Y.NYB | Spot/cash | Dollar index. `DX=F` futures preferred but unavailable on yfinance. Small discrepancy vs Finviz. |
| Put/Call | CNN F&G API `put_and_call_options.score` | Derived | CNN-normalised CBOE ratio 0-100. Delta vs last known value, persisted to disk across restarts. |
| F&G Stocks | production.dataviz.cnn.io | Composite | CNN equity Fear & Greed. Delta from `previous_close`. Rating abbreviated. |

**F&G Stocks — 7 sub-indicators:**
1. Market momentum (S&P vs 125-day MA)
2. Stock price strength (52-week highs vs lows on NYSE)
3. Stock price breadth (advancing vs declining volume)
4. Put/Call options (CBOE ratio)
5. Junk bond demand (spread between high-yield and investment-grade)
6. Market volatility (VIX vs 50-day MA)
7. Safe haven demand (stock vs bond returns)

Contrarian signal at extremes: below 25 = long-term value buyers historically step in. Above 75 = market most vulnerable to pullback.

**Put/Call sourcing:** CBOE scraping blocked (403). yfinance tickers ^PCCR, ^CPC, ^CPCE all return empty. CNN F&G `put_and_call_options` top-level key is the only working free source.

---

### 2. Equity Futures & Indices

US indices use futures (24/7, captures overnight risk). International use cash (stale when markets closed).

| Label | Ticker | Type |
|-------|--------|------|
| S&P 500 | ^GSPC | Cash | Switched from ES=F — futures % change was misleading (measures vs futures settlement, not 4pm cash close). Cash matches Bloomberg/Finviz. Stale outside market hours. |
| NASDAQ 100 | ^NDX | Cash | Switched from NQ=F — same reason. Label updated from "NASDAQ" to "NASDAQ 100" for clarity. |
| Nikkei | ^N225 | Cash |
| EuroStoxx | ^STOXX50E | Cash |
| DAX | ^GDAXI | Cash |
| KOSPI | ^KS11 | Cash |
| CSI 300 | 000300.SS | Cash |

---

### 3. Rates

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

| Label | Ticker/Source | Reference levels |
|-------|--------------|-----------------|
| MOVE Index | ^MOVE | Normal <80. Elevated 80–100. Stress 100–150. Crisis >150. (COVID peak ~160, 2023 banking crisis ~140) |
| HYG | HYG | Normal $76–$82. Stress $70–$76. Crisis <$70. (COVID low ~$68, 2022 low ~$70) |
| JNK | JNK | Normal $92–$100. Stress $85–$92. Crisis <$85. Confirms HYG. |
| HYG/TLT | fetch_ratio("HYG","TLT") | Direction matters more than level. Sustained decline = credit warning ahead of equities. |
| TLT | TLT | Inverse of long rates. TLT up + equities down = risk-off. TLT down + equities up = reflation. |

**Why this row matters:** Bond and credit markets price risk before equities. MOVE and HYG/TLT divergences from equity indices are early warning signals for rebalancing vs reversal classification.

---

### 5. Breadth

| Label | Ticker/Source | Notes |
|-------|--------------|-------|
| RSP | RSP | Equal-weight S&P 500 ETF |
| SPY | SPY | Market-cap weighted S&P 500 ETF |
| RSP/SPY | fetch_ratio("RSP","SPY") | Breadth indicator. Rising = broad participation. Falling = mega-cap driven, fragile rally. |

**How to read RSP/SPY:** If SPY is up but RSP/SPY is falling, the index gain is driven by a handful of large-cap names. The underlying market is weakening.

---

### 6. Macro Data

All FRED data uses the JSON API (`api.stlouisfed.org/fred/series/observations`) with API key `FRED_API_KEY`. Cached in session_state for 1 hour. FRED parallel threads write to session_state before page renders. ZQ=F fetched inline (not in thread) because Streamlit silently blocks session_state writes from background threads.

| Label | Source | Frequency | Reference levels |
|-------|--------|-----------|-----------------|
| Fed Funds Implied | ZQ=F (yfinance, inline) | Live | Formula: 100 minus futures price. Compare to FOMC target. Gap = market pricing cuts/hikes. |
| Jobless Claims | FRED: ICSA | Weekly (Thu 8:30am ET) | Healthy <220k. Normal 220–260k. Elevated 260–300k. Concern 300–400k. Recession signal >400k sustained. |
| CPI YoY | FRED: CPIAUCSL | Monthly | YoY % via `fetch_fred_yoy()` — obs[-1] vs obs[-13]. Fed target ~2%. Cooling 2–3%. Hot 3–5%. Crisis >6%. |
| NFP MoM | FRED: PAYEMS | Monthly (first Fri) | `fetch_fred_mom()` — obs[-1] minus obs[-2]. Strong >+250k. Healthy +150–250k. Weak <+50k. Recession = negative. |

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
- S&P 500 and NASDAQ 100: switched to cash (^GSPC, ^NDX) — go stale outside market hours. Futures (ES=F, NQ=F) had misleading % change (measured vs futures settlement not 4pm close).
- FRED next release dates: requires FRED release calendar API endpoint. Add when needed.
- Sector ETF flow row: planned next build. Will need `fetch_with_volume()` for price + volume vs 20-day avg.
- Events calendar: planned future build. Will consume `release_date` and `next_date` fields.
- Jobless Claims: shows raw weekly number — 4-week moving average would add more signal. Future improvement.

## Refresh Rate
- **Current: 120 seconds (2 minutes).** FRED data cached 1hr in session_state — refresh only re-fetches yfinance and CNN calls.

## FRED API
- Endpoint: `https://api.stlouisfed.org/fred/series/observations?series_id=X&api_key=KEY&file_type=json&sort_order=asc`
- CSV endpoint (`fred.stlouisfed.org/graph/fredgraph.csv`) times out on user's network — JSON API used instead.
- API key stored as `FRED_API_KEY` constant in `dashboard.py`.

## Put/Call Persistence
- Previous day value stored in `macro-app/.pc_prev.json` as `{"score": X, "date": "YYYY-MM-DD"}`.
- On each fetch: load file → if date is a previous calendar day, use as reference → save today's value only once (first fetch of the day, will not overwrite).
- File committed to GitHub so it persists across machines and fresh clones.
- To manually set yesterday's reference: update `score` and `date` in the file and push.
- CNN API provides `previous_close` for the composite F&G score but NOT for `put_and_call_options` sub-component — disk persistence is the only way to get a cross-session delta.

## Change Log
| Date | Change |
|------|--------|
| 2026-06-10 | Switch FRED from CSV to JSON API with key — CSV timed out on user network |
| 2026-06-10 | ZQ=F (Fed Funds) moved to inline fetch — Streamlit silently blocks session_state writes from background threads |
| 2026-06-10 | Put/Call delta persisted to `.pc_prev.json` — survives restarts, compares vs previous calendar day |
| 2026-06-11 | S&P 500 switched from ES=F to ^GSPC — futures % change was misleading (vs settlement not 4pm close) |
| 2026-06-11 | NASDAQ switched from NQ=F to ^NDX, label updated to "NASDAQ 100" |
| 2026-06-11 | `.pc_prev.json` tracked in GitHub repo — persists across machines and fresh clones |
| 2026-06-11 | Put/Call save logic fixed — date-keyed, locks reference on first fetch of day, does not overwrite within same calendar day |
