import streamlit as st
import yfinance as yf
import time

st.title("Macro Dashboard")

def fetch(ticker):
    try:
        data = yf.Ticker(ticker)
        price = round(data.fast_info['last_price'], 2)
        prev = round(data.fast_info['previous_close'], 2)
        delta = round(price - prev, 2)
        pct = round((delta / prev) * 100, 2) if prev else 0
        return price, delta, pct
    except:
        return None, None, None

def show_metric(label, ticker, help_text, show_pct=False):
    price, delta, pct = fetch(ticker)
    if price is None:
        st.metric(label=label, value="unavailable", help=help_text)
    else:
        lbl = f"{label}  ({'+' if pct >= 0 else ''}{pct}%)" if show_pct else label
        st.metric(label=lbl, value=price, delta=f"{delta} ({'+' if pct >= 0 else ''}{pct}%)", help=help_text)

# --- RISK SENTIMENT ---
st.markdown("### Risk Sentiment")
c1, c2, c3 = st.columns(3)
with c1:
    show_metric("VIX", "^VIX", "Fear index. Below 15 = calm. 15-25 = caution. Above 25 = fear. Above 30 = panic.")
with c2:
    show_metric("Dollar Index", "DX-Y.NYB", "USD strength. Rising = risk-off or strong US growth. Falling = risk-on.")
with c3:
    show_metric("Put/Call Ratio", "^PCCE", "Equity put/call ratio. Below 0.7 = complacency. Above 1.0 = fear.")

# --- US EQUITY FUTURES ---
st.markdown("### US Equity Futures")
c1, c2 = st.columns(2)
with c1:
    show_metric("S&P 500 Futures", "ES=F", "S&P 500 futures. Trades 24/7, most useful pre-market.", show_pct=True)
with c2:
    show_metric("NASDAQ Futures", "NQ=F", "NASDAQ 100 futures. Leads tech/growth sentiment.", show_pct=True)

# --- GLOBAL INDICES ---
st.markdown("### Global Indices")
c1, c2, c3 = st.columns(3)
with c1:
    show_metric("Nikkei 225", "^N225", "Japan. Leads Asian session. Sensitive to USD/JPY and global risk.", show_pct=True)
with c2:
    show_metric("EuroStoxx 50", "^STOXX50E", "Europe's benchmark. Sensitive to EUR, ECB policy, energy prices.", show_pct=True)
with c3:
    show_metric("DAX", "^GDAXI", "Germany. Export-heavy, sensitive to China growth and EUR strength.", show_pct=True)
c1, c2 = st.columns(2)
with c1:
    show_metric("KOSPI", "^KS11", "South Korea. Tech and export bellwether for Asia.", show_pct=True)
with c2:
    show_metric("CSI 300", "000300.SS", "China large cap. Key gauge of Chinese domestic economy.", show_pct=True)

# --- RATES ---
st.markdown("### Rates")
c1, c2, c3 = st.columns(3)
with c1:
    show_metric("10yr Yield", "^TNX", "10-year Treasury. Rising = growth/inflation up. Falling = safety bid.")
with c2:
    show_metric("2yr Yield", "^IRX", "2-year Treasury. 2yr > 10yr = inverted curve = recession signal.")
with c3:
    p10, _, _ = fetch("^TNX")
    p2, _, _ = fetch("^IRX")
    if p10 and p2:
        spread = round(p10 - p2, 2)
        color = "normal" if spread >= 0 else "inverse"
        st.metric(label="Yield Spread (10yr-2yr)", value=spread, help="Positive = normal curve. Negative = inverted = recession warning.")
    else:
        st.metric(label="Yield Spread (10yr-2yr)", value="unavailable")

# --- COMMODITIES ---
st.markdown("### Commodities")
c1, c2, c3, c4 = st.columns(4)
with c1:
    show_metric("Oil WTI", "CL=F", "West Texas crude. Key driver for Energy sector and inflation expectations.")
with c2:
    show_metric("Gold", "GC=F", "Safe haven. Rising = risk-off, inflation hedge, or dollar weakness.")
with c3:
    show_metric("Silver", "SI=F", "Industrial + safe haven hybrid. Tracks gold but more volatile.")
with c4:
    show_metric("Copper", "HG=F", "Dr Copper. Leading indicator of global economic health. Rising = growth.")

# --- CRYPTO ---
st.markdown("### Crypto")
c1, c2 = st.columns(2)
with c1:
    show_metric("Bitcoin", "BTC-USD", "Risk-on asset. Tracks nasdaq in risk-off, acts as digital gold in inflation.")
with c2:
    show_metric("Ethereum", "ETH-USD", "Tracks BTC but higher beta. Sensitive to DeFi and tech sentiment.")

# --- CURRENCIES ---
st.markdown("### Currencies")
c1, c2, c3, c4 = st.columns(4)
with c1:
    show_metric("EUR/USD", "EURUSD=X", "Euro vs Dollar. Falling = dollar strength / risk-off.")
with c2:
    show_metric("JPY/USD", "JPY=X", "Yen vs Dollar. Yen rising = risk-off safe haven bid.")
with c3:
    show_metric("GBP/USD", "GBPUSD=X", "Pound vs Dollar. Sensitive to UK macro and global risk appetite.")
with c4:
    show_metric("USD/CNY", "USDCNY=X", "Dollar vs Chinese Yuan. Rising = yuan weakening, often signals China stress.")

time.sleep(30)
st.rerun()
