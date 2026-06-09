# Code Logic — Macro App

This document maps each section of `dashboard.py` to the corresponding logic in `macro-logic.md`.

For instrument selection rationale (futures vs spot) see the discussion in session notes.

---

## Architecture

`dashboard.py` is structured as a single-page Streamlit app with 6 sections, each rendered as a horizontal row of fixed-width (160px) metric cards. All data is fetched live via `yfinance` on page load and refreshes every 30 seconds via `st.rerun()`.

### Key functions
- `fetch(ticker)` — fetches last price, previous close, delta, and % change for any ticker
- `show_metric(col, label, ticker, help_text)` — renders a single metric card with delta and tooltip

---

## Sections

### 1. Risk Sentiment
**Logic ref:** `macro-logic.md` → Inputs → Price/Market, and Classification Logic context layer

| Label | Ticker | Type | Purpose |
|-------|--------|------|---------|
| VIX | ^VIX | Spot | Fear gauge. Spot used — VIX futures behave differently from spot index |
| DXY | DX=F | Futures | Dollar strength. Futures used as institutional baseline |
| Put/Call | ^PCCE | Spot | Options sentiment. Equity-only ratio |

---

### 2. Equity Futures & Indices
**Logic ref:** `macro-logic.md` → Inputs → Price/Market

US indices use futures (captures overnight macro risk). International indices use cash (futures not reliably available on yfinance).

| Label | Ticker | Type | Notes |
|-------|--------|------|-------|
| S&P 500 | ES=F | Futures | US — primary equity risk indicator |
| NASDAQ | NQ=F | Futures | US — leads tech/growth sentiment |
| Nikkei | ^N225 | Cash index | Japan — shows Asian session direction |
| EuroStoxx | ^STOXX50E | Cash index | Europe benchmark |
| DAX | ^GDAXI | Cash index | Germany — export/China proxy |
| KOSPI | ^KS11 | Cash index | South Korea — Asia tech bellwether |
| CSI 300 | 000300.SS | Cash index | China domestic economy gauge |

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
- Put/Call Ratio (^PCCE) intermittently unavailable via yfinance — alternative source TBD
- International equity indices use cash prices — will show stale when those markets are closed
- Refresh rate: 30 seconds. May adjust based on usage patterns
