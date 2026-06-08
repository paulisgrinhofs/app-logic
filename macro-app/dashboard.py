import streamlit as st
import yfinance as yf
import time

st.title("Macro Dashboard")

COLS = 4  # fixed column width across all rows

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

def show_metric(col, label, ticker, help_text, show_pct=False):
    with col:
        price, delta, pct = fetch(ticker)
        if price is None:
            st.metric(label=label, value="unavailable", help=help_text)
        else:
            delta_str = f"{'+' if delta >= 0 else ''}{delta} ({'+' if pct >= 0 else ''}{pct}%)"
            st.metric(label=label, value=price, delta=delta_str, help=help_text)

# --- RISK SENTIMENT ---
st.markdown("### Risk Sentiment")
cols = st.columns(COLS)
show_metric(cols[0], "VIX", "^VIX", "Fear index. Below 15 = calm. 15-25 = caution. Above 25 = fear. Above 30 = panic.")
show_metric(cols[1], "Dollar Index", "DX-Y.NYB", "USD strength. Rising = risk-off or strong US growth. Falling = risk-on.")
show_metric(cols[2], "Put/Call Ratio", "^PCCE", "Equity put/call ratio. Below 0.7 = complacency. Above 1.0 = fear.")

# --- EQUITY FUTURES ---
st.markdown("### Equity Futures")
cols = st.columns(COLS)
show_metric(cols[0], "S&P 500", "ES=F", "S&P 500 futures. Trades 24/7, most useful pre-market.", show_pct=True)
show_metric(cols[1], "NASDAQ", "NQ=F", "NASDAQ 100 futures. Leads tech/growth sentiment.", show_pct=True)
show_metric(cols[2], "Nikkei 225", "^N225", "Japan. Leads Asian session. Sensitive to USD/JPY and global risk.", show_pct=True)
show_metric(cols[3], "EuroStoxx 50", "^STOXX50E", "Europe benchmark. Sensitive to EUR, ECB policy, energy prices.", show_pct=True)
cols = st.columns(COLS)
show_metric(cols[0], "DAX", "^GDAXI", "Germany. Export-heavy, sensitive to China growth and EUR.", show_pct=True)
show_metric(cols[1], "KOSPI", "^KS11", "South Korea. Tech and export bellwether for Asia.", show_pct=True)
show_metric(cols[2], "CSI 300", "000300.SS", "China large cap. Key gauge of Chinese domestic economy.", show_pct=True)

# --- RATES ---
st.markdown("### Rates")
cols = st.columns(COLS)
show_metric(cols[0], "10yr Yield", "^TNX", "10-year Treasury. Rising = growth/inflation up. Falling = safety bid.")
show_metric(cols[1], "2yr Yield", "^IRX", "2-year Treasury. 2yr > 10yr = inverted curve = recession signal.")
show_metric(cols[2], "30yr Yield", "^TYX", "30-year Treasury. Long-end rates. Sensitive to inflation expectations.")
p10, _, _ = fetch("^TNX")
p2, _, _ = fetch("^IRX")
if p10 and p2:
    spread = round(p10 - p2, 2)
    with cols[3]:
        st.metric(label="Spread (10yr-2yr)", value=spread, help="Positive = normal curve. Negative = inverted = recession warning.")
else:
    with cols[3]:
        st.metric(label="Spread (10yr-2yr)", value="unavailable")

# --- COMMODITIES ---
st.markdown("### Commodities")
cols = st.columns(COLS)
show_metric(cols[0], "Crude WTI", "CL=F", "WTI crude oil. US benchmark. Key for Energy sector and inflation.")
show_metric(cols[1], "Crude Brent", "BZ=F", "Brent crude. Global benchmark. Slightly higher than WTI typically.")
show_metric(cols[2], "Gold", "GC=F", "Safe haven. Rising = risk-off, inflation hedge, or dollar weakness.")
show_metric(cols[3], "Silver", "SI=F", "Industrial + safe haven hybrid. Tracks gold but more volatile.")
cols = st.columns(COLS)
show_metric(cols[0], "Copper", "HG=F", "Dr Copper. Leading indicator of global economic health. Rising = growth.")

# --- CRYPTO ---
st.markdown("### Crypto")
cols = st.columns(COLS)
show_metric(cols[0], "Bitcoin", "BTC-USD", "Risk-on asset. Tracks NASDAQ in risk-off, acts as digital gold in inflation.")
show_metric(cols[1], "Ethereum", "ETH-USD", "Tracks BTC but higher beta. Sensitive to DeFi and tech sentiment.")

# --- CURRENCIES ---
st.markdown("### Currencies")
cols = st.columns(COLS)
show_metric(cols[0], "EUR/USD", "EURUSD=X", "Euro vs Dollar. Falling = dollar strength / risk-off.")
show_metric(cols[1], "USD/JPY", "JPY=X", "Dollar vs Yen. Rising = risk-on. Falling Yen = safe haven bid.")
show_metric(cols[2], "GBP/USD", "GBPUSD=X", "Pound vs Dollar. Sensitive to UK macro and global risk appetite.")
show_metric(cols[3], "USD/CNY", "USDCNY=X", "Dollar vs Yuan. Rising = yuan weakening, often signals China stress.")

time.sleep(30)
st.rerun()
