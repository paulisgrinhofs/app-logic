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
| `_cme_front_month(prefix)` | Returns active quarterly CME equity futures ticker (e.g. `ESM26.CME`). Rolls on second Friday of expiry month. Used for S&P 500 and NASDAQ 100. |
| `_commodity_front_month(prefix, exchange, active_months, roll_day, roll_months_before)` | Returns active commodity futures ticker (e.g. `CLN26.NYM`). Per-commodity roll schedule. Used for all 6 commodity futures. |
| `fetch_ratio(t1, t2)` | Fetches ratio of two tickers (e.g. HYG/TLT, RSP/SPY) with delta vs previous close ratio |
| `_fetch_fred_raw(series_id)` | Fetches FRED observations via JSON API with API key. Returns list of `(date, float)` tuples, newest last. Cached 1hr. |
| `_prefetch_slow()` | Runs FRED fetches (ICSA, CPIAUCSL, PAYEMS) in parallel threads before page renders. Writes results to `session_state`. ZQ=F excluded — fetched inline instead (Streamlit blocks session_state writes from threads). |
| `fetch_fred(series_id, cache_key)` | Latest single value + date. Uses `_fetch_fred_raw`. Cached 1hr. |
| `fetch_fred_yoy(series_id, cache_key)` | YoY % change: `obs[-1]` vs `obs[-13]`. Used for CPI. Returns `(value, yoy_pct, date)`. Cached 1hr. |
| `fetch_fred_mom(series_id, cache_key)` | Month-on-month change: `obs[-1]` minus `obs[-2]`. Used for NFP. Returns `(value, mom, date)`. Cached 1hr. |
| `fetch_uranium()` | FRED PURANUSDM — World Bank monthly uranium spot price. Delta = month-on-month. Cached 1hr in session_state. |
| `fetch_put_call()` | CNN F&G API `put_and_call_options.score`. Delta vs previous day via `.daily_cache.json`. |
| `_load_daily_cache()` | Reads `.daily_cache.json` — unified file for all cross-session persistent values. |
| `_save_daily_cache(data)` | Writes updated dict to `.daily_cache.json`. |
| `_daily_prev(key)` | Returns yesterday's value for a given key from `.daily_cache.json`. |
| `_daily_update(key, value)` | Updates today's value for a key; rolls today→prev at midnight. |
| `_load_pc_prev()` | Thin wrapper — calls `_daily_prev("put_call")`. |
| `_save_pc_prev(score)` | Thin wrapper — calls `_daily_update("put_call", score)`. |
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

US indices use specific CME contract tickers (auto-detected by `_cme_front_month()`). International use cash (stale when markets closed — industry standard).

**Delta methodology:** current price vs yesterday's official CME settlement price of the same contract. Matches Finviz/Bloomberg. Continuous rolling tickers (ES=F, NQ=F) were replaced because Yahoo Finance splices contracts on quarterly roll days, creating phantom % gaps that never happened in the market.

| Label | Ticker | Type |
|-------|--------|------|
| S&P 500 | ESM26.CME (auto) | Futures | Specific front-month contract, auto-rolls quarterly. % change vs prior CME settlement. |
| NASDAQ 100 | NQM26.CME (auto) | Futures | Same. |
| Nikkei | ^N225 | Cash | Stale when Tokyo closed — industry standard behaviour. |
| EuroStoxx | ^STOXX50E | Cash | Stale when European session closed. |
| DAX | ^GDAXI | Cash | Stale when Frankfurt closed. |
| KOSPI | ^KS11 | Cash | Stale when Seoul closed. |
| CSI 300 | 000300.SS | Cash | Stale when Shanghai closed. |

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

**Delta methodology:** all commodity futures use specific front-month contract tickers via `_commodity_front_month()`. Delta = current price vs prior CME/NYMEX settlement of the same contract. Continuous tickers (CL=F etc.) replaced — Yahoo Finance splices contracts on roll days creating phantom gaps. Roll schedules are per-commodity and auto-calculated.

| Label | Ticker (auto) | Exchange | Roll | Purpose |
|-------|--------------|----------|------|---------|
| WTI Crude | CLN26.NYM (auto) | NYMEX | Monthly, ~day 20 of prior month. All 12 months trade. | US oil benchmark + inflation signal |
| Brent Crude | BZQ26.NYM (auto) | NYMEX | Monthly, expires end of 2nd month before delivery — rolls earlier than WTI | Global benchmark |
| Gold | GCQ26.CMX (auto) | COMEX | Even months (Feb/Apr/Jun/Aug/Oct/Dec), rolls ~day 25 of prior month | Safe haven / inflation hedge / dollar inverse |
| Silver | SIN26.CMX (auto) | COMEX | Jan/Mar/May/Jul/Sep/Dec, rolls ~day 25 of prior month | Industrial + safe haven hybrid |
| Copper | HGN26.CMX (auto) | COMEX | Mar/May/Jul/Sep/Dec, rolls ~day 25 of prior month | Global growth leading indicator. Price in USD per lb. Normal: 3.50–4.50. |
| Aluminium | ALIN26.CMX (auto) | COMEX | Jan/Mar/May/Jul/Sep/Dec, rolls ~day 25 of prior month | Industrial metal. Price in USD per metric tonne. Normal: 2,000–2,650. |
| Uranium | FRED: PURANUSDM | FRED | Monthly release — no roll issue | World Bank global uranium spot benchmark ($/lb U₃O₈). Delta = month-on-month. Normal: $40–$65. Elevated: $65–$100. Crisis: >$100. |

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

## Nasdaq Data Link API
- Key: `NASDAQ_DATA_LINK_KEY` constant in `dashboard.py`. Key: `GuzsYWXo26kTjhcNnj9B`.
- Base URL: `https://data.nasdaq.com/api/v3/datasets/{DATABASE}/{SERIES}/data?api_key=KEY&limit=N&order=desc`
- **Free tier includes:** equities (WIKI, EOD, NAEOD), some economic data. 50 calls/day limit.
- **CHRIS database (CME continuous futures) requires paid subscription** — confirmed blocked at account level via Imperva/Incapsula 403. UX1! uranium futures, and all other CME continuous futures, unavailable on free tier.
- Currently unused in dashboard — uranium switched to FRED PURANUSDM. Key retained for future use with free-tier datasets (equity data etc.).

## FRED API
- Endpoint: `https://api.stlouisfed.org/fred/series/observations?series_id=X&api_key=KEY&file_type=json&sort_order=asc`
- CSV endpoint (`fred.stlouisfed.org/graph/fredgraph.csv`) times out on user's network — JSON API used instead.
- API key stored as `FRED_API_KEY` constant in `dashboard.py`.

## Daily Cache (`macro-app/.daily_cache.json`)
Single unified file for all cross-session persistent data. Replaces `.pc_prev.json`.

Structure:
```json
{
  "put_call": {"prev": 34.0, "today": 26.0, "today_date": "2026-06-11"},
  "uranium":  {"prev": null, "today": 65.5, "today_date": "2026-06-11"}
}
```

Logic (shared `_daily_update(key, value)` / `_daily_prev(key)`):
- Each key has `prev` (yesterday, read-only during the day) and `today`/`today_date` (updated every fetch)
- At midnight rollover: `today` promotes to `prev` automatically
- File committed to GitHub — persists across machines and fresh clones
- To manually set a reference value: edit `prev` for the relevant key and push

Adding a new data source: add a new key to `.daily_cache.json`, call `_daily_prev("key")` to read and `_daily_update("key", value)` to write.

CNN API provides `previous_close` for composite F&G but NOT for `put_and_call_options` — disk persistence is the only way to get a cross-session delta for Put/Call.

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
| 2026-06-11 | Added Uranium (UX1!) to commodities — CME front-month futures via Nasdaq Data Link free tier (CHRIS/CME_UX1). Cached 24hr. API key: NASDAQ_DATA_LINK_KEY constant. |
| 2026-06-11 | Fixed Python 3.14 asyncio crash — FRED threads write to plain dict, copy to session_state on main thread; st.rerun() wrapped in try/except |
| 2026-06-11 | Unified daily cache — .pc_prev.json replaced by .daily_cache.json; all cross-session persistent data in one file; extendable with new keys |
| 2026-06-11 | Uranium switched from Nasdaq Data Link CHRIS/CME_UX1 to FRED PURANUSDM — CHRIS requires paid subscription, blocked by Imperva at account level |
| 2026-06-11 | meta http-equiv refresh reverted — was breaking yfinance fetches by reloading browser mid-request; restored time.sleep(120) + st.rerun() |
| 2026-06-11 | Uranium added to FRED prefetch threads (PURANUSDM); delta = month-on-month |
| 2026-06-11 | Added Aluminium (ALI=F) to commodities between Copper and Uranium |
| 2026-06-11 | Fixed Python 3.14 asyncio crash — replaced time.sleep+st.rerun() with streamlit-autorefresh (JS-based interval, no event loop conflict) |
| 2026-06-11 | Known issue: git pull does not restore .daily_cache.json if dashboard has modified it locally. Workaround: run `git checkout macro-app/.daily_cache.json && git pull` before starting dashboard to restore prev reference values. |
| 2026-06-12 | Added TW ticker symbols to all tooltips for quick TradingView lookup. Fixed Copper/Aluminium reference levels ($/lb and $/metric tonne). |
| 2026-06-12 | Investigated S&P/NASDAQ % mismatch vs Finviz — root cause: ^GSPC/^NDX show prior cash close (stale overnight), ES=F/NQ=F have roll-day splicing artifacts. Fix: auto-detect active CME front-month contract (ESM26.CME / NQM26.CME format). _cme_front_month() function rolls automatically on second Friday of expiry month. % change now matches Finviz/Bloomberg methodology (vs prior CME settlement). |
| 2026-06-12 | Fixed commodity futures % change — same roll-splicing problem as ES/NQ but monthly. Added _commodity_front_month() function with per-commodity roll schedules. WTI/Brent: .NYM exchange, all 12 months. Gold/Silver/Copper/Aluminium: .CMX exchange. Brent rolls 2 months before delivery (expires earlier than WTI). Confirmed ticker formats via live test: CLN26.NYM, BZQ26.NYM, GCQ26.CMX, SIN26.CMX, HGN26.CMX, ALIN26.CMX. Uranium excluded — FRED data, not yfinance futures. |
