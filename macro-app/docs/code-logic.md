# Code Logic — Macro App

This document maps each section of code in `dashboard.py` to the corresponding logic in `macro-logic.md`.

---

## Market Inputs
**Code:** `tickers` dict + loop in `dashboard.py`  
**Logic ref:** `macro-logic.md` → Inputs → Price/Market  
**Purpose:** Displays all key market inputs in one place — VIX, futures, yields, dollar, oil, put/call ratio

### VIX
Fear level indicator. Context layer for risk-on/risk-off reading.

### S&P 500 Futures / NASDAQ Futures
Pre-market equity direction.

### 10yr Yield / 2yr Yield
10yr = rates context. 2yr vs 10yr spread = yield curve / recession signal.

### Dollar Index (DXY)
Safe-haven demand indicator. Rising DXY in risk-off = flight to safety.

### Oil WTI
Key driver for Energy sector. Also feeds inflation expectations.

### Put/Call Ratio
Options market sentiment. High = fear, low = complacency.
