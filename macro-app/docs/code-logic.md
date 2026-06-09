# Code Logic — Macro App

This document maps each section of `dashboard.py` to the corresponding logic in `macro-logic.md`.

---

## Architecture

`dashboard.py` is a single-page Streamlit app with 6 sections, each rendered as a horizontal row of fixed-width (160px) metric cards. Data fetched via `yfinance` and `requests`, refreshing every 30 seconds via `st.rerun()`.

### Key functions
- `fetch(ticker)` — fetches last price, previous close, delta, % change via yfinance `fast_info`
- `fetch_put_call()` — extracts Put/Call sub-component from CNN F&G API (`put_and_call_options.score`)
- `fetch_fear_greed_cnn()` — fetches CNN stock Fear & Greed from `production.dataviz.cnn.io` with User-Agent header
- `fetch_fear_greed_crypto()` — fetches crypto Fear & Greed from `api.alternative.me/fng/`
- `show_metric(col, label, ticker, help_text)` — renders metric card with delta, % change, tooltip

---

## Sections

### 1. Risk Sentiment
**Logic ref:** `macro-logic.md` → Inputs → Price/Market, Classification Logic context layer

| Label | Ticker/Source | Type | Notes |
|-------|--------------|------|-------|
| VIX | ^VIX | Spot | Fear gauge. Spot used — VIX futures behave differently |
| DXY | DX-Y.NYB | Spot/cash | Dollar index. `DX=F` futures preferred but not available on yfinance. Small discrepancy vs Finviz which uses `DX=F`. |
| Put/Call | CNN F&G API — `put_and_call_options.score` | Derived | CNN-normalised CBOE ratio on 0-100 scale. Higher = more calls vs puts = bullish. Lower = more puts vs calls = bearish hedging. Raw CBOE >1.0 = more puts. Contrarian indicator — extremes mark turning points. |
| F&G Stocks | `production.dataviz.cnn.io/index/fearandgreed/graphdata` | Composite | CNN stock market Fear & Greed 0-100. Score shown as value, rating as label below. |

**F&G Stocks — how to read:** Composite of 7 equal-weight sub-indicators:
1. Market momentum (S&P vs 125-day MA)
2. Stock price strength (52-week highs vs lows on NYSE)
3. Stock price breadth (advancing vs declining volume)
4. Put/Call options (CBOE ratio)
5. Junk bond demand (spread between high-yield and investment-grade)
6. Market volatility (VIX vs 50-day MA)
7. Safe haven demand (stock vs bond returns)

Each sub-indicator scored 0-100 → averaged to composite. Score reflects crowd sentiment, not fundamentals. Use as contrarian signal at extremes (below 25 or above 75).

**F&G (Crypto)** moved to Crypto section — separate index (alternative.me) tracking Bitcoin market sentiment only. Not an equity signal.

**Put/Call sourcing history:** CBOE direct scraping blocked (403). yfinance tickers ^PCCR, ^CPC, ^CPCE all return empty data. CNN F&G API `put_and_call_options` top-level key is the only working free source.

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

| Label | Ticker/Source | Purpose |
|-------|--------------|---------|
| Bitcoin | BTC-USD | Risk-on/off signal + digital gold proxy |
| Ethereum | ETH-USD | Higher beta crypto, DeFi/tech sentiment |
| F&G (Crypto) | api.alternative.me/fng/ | Crypto-only sentiment index. Inputs: volatility, momentum/volume, social media, dominance, Google trends. Placed here not in Risk Sentiment — it measures crypto market mood, not equity market mood. |

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
