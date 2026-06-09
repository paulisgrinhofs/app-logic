# Code Logic — Macro App

This document maps each section of `dashboard.py` to the corresponding logic in `macro-logic.md`.

---

## Architecture

`dashboard.py` is a single-page Streamlit app with 6 sections, each rendered as a horizontal row of fixed-width (160px) metric cards. Data fetched via `yfinance` and `requests`, refreshing every 30 seconds via `st.rerun()`.

### Key functions
- `fetch(ticker)` — fetches last price, previous close, delta, % change via yfinance
- `fetch_put_call()` — fetches CBOE Total Put/Call Ratio via `^PCCR` yfinance ticker (history method)
- `fetch_fear_greed_cnn()` — fetches CNN stock market Fear & Greed from feargreedchart.com (with User-Agent header)
- `fetch_fear_greed_crypto()` — fetches crypto Fear & Greed from api.alternative.me/fng/
- `show_metric(col, label, ticker, help_text)` — renders metric card with delta, % change, tooltip

---

## Sections

### 1. Risk Sentiment
**Logic ref:** `macro-logic.md` → Inputs → Price/Market, Classification Logic context layer

| Label | Ticker/Source | Type | Notes |
|-------|--------------|------|-------|
| VIX | ^VIX | Spot | Fear gauge. Spot used — VIX futures behave differently |
| DXY | DX-Y.NYB | Spot/cash | Dollar index. `DX=F` futures preferred but not available on yfinance. Small discrepancy vs Finviz which uses `DX=F`. |
| Put/Call (PCCR) | ^PCCR | yfinance | CBOE Total Put/Call Ratio. Uses `.history(period="2d")` — not `fast_info`. Above 1.0 = bearish hedging. Below 0.7 = complacency. |
| F&G (Stocks) | feargreedchart.com | Composite | CNN stock market Fear & Greed 0-100. Requires User-Agent header to avoid 403. |
| F&G (Crypto) | api.alternative.me/fng/ | Composite | **Crypto-specific** — tracks Bitcoin sentiment only, not equity markets. Shown for cross-asset context. |

**Put/Call note:** `^PCCR` is the CBOE Total Put/Call Ratio. Direct scraping of CBOE was blocked (403). This ticker uses yfinance `.history()` which accesses Yahoo's cached data — may lag slightly.

**Fear & Greed note:** CNN endpoint was returning errors without a browser User-Agent header. Added header to fix. Crypto F&G is a separate index (alternative.me) and should not be conflated with the stock market version.

**Known discrepancy:** DXY shows slightly different value vs Finviz — Finviz uses `DX=F` futures, we use `DX-Y.NYB` spot.

---

### 2. Equity Futures & Indices
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

US indices use futures (captures overnight macro risk). International indices use cash (futures not reliably available on yfinance).

| Label | Ticker | Type | Notes |
|-------|--------|------|-------|
| S&P 500 | ES=F | Futures | US — primary equity risk indicator |
| NASDAQ | NQ=F | Futures | US — leads tech/growth sentiment |
| Nikkei | ^N225 | Cash index | Japan. Stale when market closed. |
| EuroStoxx | ^STOXX50E | Cash index | Europe benchmark. Stale when market closed. |
| DAX | ^GDAXI | Cash index | Germany — export/China proxy. Stale when market closed. |
| KOSPI | ^KS11 | Cash index | South Korea. Stale when market closed. |
| CSI 300 | 000300.SS | Cash index | China domestic economy. Stale when market closed. |

---

### 3. Rates
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

All spot yields. Futures not used — spot yields are the pure cost-of-capital baseline.

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

Spot prices. Price discovery on 24/7 spot exchanges, not CME futures.

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
- DXY: using spot `DX-Y.NYB` — small discrepancy vs Finviz (`DX=F`). Fix when alternative source found.
- International equity indices: cash prices, stale when markets closed
- Refresh rate: 30 seconds
