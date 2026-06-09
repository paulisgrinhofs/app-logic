# Code Logic — Macro App

This document maps each section of `dashboard.py` to the corresponding logic in `macro-logic.md`.

For instrument selection rationale (futures vs spot) see the discussion in session notes.

---

## Architecture

`dashboard.py` is structured as a single-page Streamlit app with 6 sections, each rendered as a horizontal row of fixed-width (160px) metric cards. Data is fetched live via `yfinance` and `requests` on page load, refreshing every 30 seconds via `st.rerun()`.

### Key functions
- `fetch(ticker)` — fetches last price, previous close, delta, and % change via yfinance
- `fetch_put_call()` — scrapes CBOE daily stats page for total put/call ratio
- `show_metric(col, label, ticker, help_text)` — renders a metric card with delta, % change, and tooltip

---

## Sections

### 1. Risk Sentiment
**Logic ref:** `macro-logic.md` → Inputs → Price/Market, and Classification Logic context layer

| Label | Ticker | Type | Notes |
|-------|--------|------|-------|
| VIX | ^VIX | Spot | Fear gauge. Spot used — VIX futures behave differently from spot index |
| DXY | DX-Y.NYB | Spot/cash | Dollar index. `DX=F` futures preferred but not reliably available on yfinance. Finviz uses `DX=F` which causes small price discrepancy. |
| Put/Call | CBOE page | Scraped | Total put/call ratio fetched directly from CBOE daily stats. yfinance tickers (^CPC, ^PCCE) unreliable. |

**Known discrepancy:** DXY will show slightly different value vs Finviz because Finviz uses `DX=F` futures while we use `DX-Y.NYB` spot. Direction and story are the same.

---

### 2. Equity Futures & Indices
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

US indices use futures (captures overnight macro risk). International indices use cash (futures not reliably available on yfinance).

| Label | Ticker | Type | Notes |
|-------|--------|------|-------|
| S&P 500 | ES=F | Futures | US — primary equity risk indicator |
| NASDAQ | NQ=F | Futures | US — leads tech/growth sentiment |
| Nikkei | ^N225 | Cash index | Japan — shows Asian session direction. Stale when market closed. |
| EuroStoxx | ^STOXX50E | Cash index | Europe benchmark. Stale when market closed. |
| DAX | ^GDAXI | Cash index | Germany — export/China proxy. Stale when market closed. |
| KOSPI | ^KS11 | Cash index | South Korea — Asia tech bellwether. Stale when market closed. |
| CSI 300 | 000300.SS | Cash index | China domestic economy gauge. Stale when market closed. |

---

### 3. Rates
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

All spot yields. Futures not used — spot yields are the pure cost-of-capital baseline with no roll/expiration noise.

| Label | Ticker | Purpose |
|-------|--------|---------|
| 2yr Yield | ^IRX | Fed expectations proxy |
| 5yr Yield | ^FVX | Mid-curve |
| 10yr Yield | ^TNX | Global benchmark rate |
| 30yr Yield | ^TYX | Long-end inflation expectations |
| Spread (10-2yr) | calculated | Yield curve shape. Negative = inverted = recession signal |

---

### 4. Commodity Futures
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

All futures. Commodity futures show supply/demand structure and are the institutional benchmark.

| Label | Ticker | Purpose |
|-------|--------|---------|
| WTI Crude | CL=F | US oil benchmark. Energy sector driver + inflation signal |
| Brent Crude | BZ=F | Global oil benchmark |
| Gold | GC=F | Safe haven / inflation hedge / dollar inverse |
| Silver | SI=F | Industrial + safe haven hybrid |
| Copper | HG=F | Global growth leading indicator |

---

### 5. Crypto
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

Spot prices used. Crypto price discovery happens on 24/7 spot exchanges, not CME futures.

| Label | Ticker | Purpose |
|-------|--------|---------|
| Bitcoin | BTC-USD | Risk-on/off signal + digital gold proxy |
| Ethereum | ETH-USD | Higher beta crypto, DeFi/tech sentiment |

---

### 6. Currencies
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

| Label | Ticker | Purpose |
|-------|--------|---------|
| EUR/USD | EURUSD=X | Euro strength vs dollar |
| USD/JPY | JPY=X | Yen as safe haven indicator |
| GBP/USD | GBPUSD=X | UK macro proxy |
| USD/CNY | USDCNY=X | Yuan strength — China stress indicator |

---

## Open Items
- DXY: using spot `DX-Y.NYB` instead of futures `DX=F` — small price discrepancy vs Finviz. To fix when alternative data source found.
- Put/Call: scraped from CBOE page — fragile if CBOE changes page structure
- International equity indices: cash prices, stale when those markets are closed
- Refresh rate: 30 seconds. May adjust based on usage
