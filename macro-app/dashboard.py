import streamlit as st
import yfinance as yf
import requests
import time

st.set_page_config(layout="wide")
st.title("Macro Dashboard")

st.markdown("""
<style>
[data-testid="stMetric"] {
    width: 160px;
    min-width: 160px;
}
[data-testid="column"] {
    width: fit-content !important;
    flex: unset !important;
    min-width: 160px !important;
    max-width: 160px !important;
}
</style>
""", unsafe_allow_html=True)

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

RATING_SHORT = {
    "Extreme Fear": "Ext Fear",
    "Extreme Greed": "Ext Greed",
    "Fear": "Fear",
    "Greed": "Greed",
    "Neutral": "Neutral",
}

def shorten_rating(rating):
    return RATING_SHORT.get(rating, rating)

def fetch_put_call():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", timeout=5, headers=headers)
        data = r.json()
        for key in ['put_and_call_options', 'put_call_options']:
            block = data.get(key, {})
            score = block.get('score')
            if score is not None:
                score = round(float(score), 1)
                # No previous_close in sub-component — use session_state to track change
                prev = st.session_state.get('pc_prev')
                st.session_state['pc_prev'] = score
                delta = round(score - prev, 1) if prev is not None else None
                pct = round((delta / prev) * 100, 1) if delta and prev else None
                return score, delta, pct
    except:
        pass
    return None, None, None

def fetch_fear_greed_cnn():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        r = requests.get(url, timeout=5, headers=headers)
        data = r.json()
        fg = data['fear_and_greed']
        score = round(fg['score'], 1)
        rating = fg['rating'].replace("_", " ").title()
        prev = fg.get('previous_close')
        delta = round(score - float(prev), 1) if prev is not None else None
        pct = round((delta / float(prev)) * 100, 1) if delta and prev else None
        return score, rating, delta, pct
    except:
        return None, None, None, None

def fetch_fear_greed_crypto():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=2", timeout=5)
        data = r.json()
        score = int(data['data'][0]['value'])
        rating = data['data'][0]['value_classification']
        prev = int(data['data'][1]['value']) if len(data['data']) > 1 else None
        delta = round(score - prev, 1) if prev is not None else None
        pct = round((delta / prev) * 100, 1) if delta and prev else None
        return score, rating, delta, pct
    except:
        return None, None, None, None

def show_metric(col, label, ticker, help_text):
    with col:
        price, delta, pct = fetch(ticker)
        if price is None:
            st.metric(label=label, value="n/a", help=help_text)
        else:
            delta_str = f"{'+' if delta >= 0 else ''}{delta} ({'+' if pct >= 0 else ''}{pct}%)"
            st.metric(label=label, value=price, delta=delta_str, help=help_text)

# --- RISK SENTIMENT ---
st.markdown("### Risk Sentiment")
cols = st.columns(8)
show_metric(cols[0], "VIX", "^VIX", "Fear index. Below 15 = calm. 15-25 = caution. Above 25 = fear. Above 30 = panic.")
show_metric(cols[1], "DXY", "DX-Y.NYB", "USD index (spot). Rising = risk-off or strong US growth. Falling = risk-on.")

pc, pc_delta, pc_pct = fetch_put_call()
with cols[2]:
    if pc is not None:
        pc_delta_str = f"{'+' if pc_delta >= 0 else ''}{pc_delta} ({'+' if pc_pct >= 0 else ''}{pc_pct}%)" if (pc_delta is not None and pc_pct is not None) else (f"{'+' if pc_delta >= 0 else ''}{pc_delta}" if pc_delta is not None else None)
        st.metric(label="Put/Call", value=pc, delta=pc_delta_str, help="CNN-normalised Put/Call ratio (0-100 scale). Source: CBOE options data via CNN F&G API. Higher = more calls vs puts = bullish. Lower = more puts vs calls = bearish hedging. Contrarian: extremes often mark turning points. Change = vs previous close.")
    else:
        st.metric(label="Put/Call", value="n/a", help="Put/Call Ratio — sourced from CNN F&G API sub-components.")

cnn_score, cnn_rating, cnn_delta, cnn_pct = fetch_fear_greed_cnn()
with cols[3]:
    if cnn_score:
        cnn_delta_str = f"{'+' if cnn_delta >= 0 else ''}{cnn_delta} ({'+' if cnn_pct >= 0 else ''}{cnn_pct}%)" if (cnn_delta is not None and cnn_pct is not None) else shorten_rating(cnn_rating)
        st.metric(label=f"F&G Stocks", value=cnn_score, delta=cnn_delta_str, help="CNN Fear & Greed Index (equity markets). Composite of 7 inputs: market momentum, stock price strength, breadth, put/call options, junk bond demand, market volatility, safe haven demand. 0-25 = Extreme Fear. 25-45 = Fear. 45-55 = Neutral. 55-75 = Greed. 75-100 = Extreme Greed. Historically below 25 = long-term value buyers step in. Above 75 = market most vulnerable to pullback. Change = vs previous close.")
    else:
        st.metric(label="F&G Stocks", value="n/a", help="CNN Fear & Greed Index for equity markets.")

# --- EQUITY FUTURES & INDICES ---
st.markdown("### Equity Futures & Indices")
cols = st.columns(8)
show_metric(cols[0], "S&P 500", "ES=F", "S&P 500 futures (ES=F). Trades 24/7, captures overnight macro risk.")
show_metric(cols[1], "NASDAQ", "NQ=F", "NASDAQ 100 futures (NQ=F). Leads tech/growth sentiment.")
show_metric(cols[2], "Nikkei", "^N225", "Japan cash index. Leads Asian session. Sensitive to USD/JPY and global risk.")
show_metric(cols[3], "EuroStoxx", "^STOXX50E", "Europe cash index. Sensitive to EUR, ECB policy, energy prices.")
show_metric(cols[4], "DAX", "^GDAXI", "Germany cash index. Export-heavy, sensitive to China growth and EUR.")
show_metric(cols[5], "KOSPI", "^KS11", "South Korea cash index. Tech and export bellwether for Asia.")
show_metric(cols[6], "CSI 300", "000300.SS", "China large cap cash index. Key gauge of Chinese domestic economy.")

# --- RATES ---
st.markdown("### Rates")
cols = st.columns(8)
show_metric(cols[0], "2yr Yield", "^IRX", "2-year Treasury spot yield. Most sensitive to Fed rate expectations.")
show_metric(cols[1], "5yr Yield", "^FVX", "5-year Treasury spot yield. Mid-range rates expectations.")
show_metric(cols[2], "10yr Yield", "^TNX", "10-year Treasury spot yield. Rising = growth/inflation up. Falling = safety bid.")
show_metric(cols[3], "30yr Yield", "^TYX", "30-year Treasury spot yield. Long-end rates. Sensitive to inflation expectations.")
p10, _, _ = fetch("^TNX")
p2, _, _ = fetch("^IRX")
p10_prev = round(yf.Ticker("^TNX").fast_info['previous_close'], 2) if p10 else None
p2_prev = round(yf.Ticker("^IRX").fast_info['previous_close'], 2) if p2 else None
with cols[4]:
    if p10 and p2:
        spread = round(p10 - p2, 2)
        if p10_prev and p2_prev:
            spread_prev = round(p10_prev - p2_prev, 2)
            spread_delta = round(spread - spread_prev, 2)
            spread_pct = round((spread_delta / abs(spread_prev)) * 100, 1) if spread_prev else None
            delta_str = f"{'+' if spread_delta >= 0 else ''}{spread_delta} ({'+' if spread_pct >= 0 else ''}{spread_pct}%)" if spread_pct is not None else f"{'+' if spread_delta >= 0 else ''}{spread_delta}"
            st.metric(label="Spread (10-2yr)", value=spread, delta=delta_str, help="10yr minus 2yr yield. Positive = normal curve. Negative = inverted = recession warning. Narrowing = curve flattening (tightening conditions). Widening = steepening (growth expectations rising or Fed cutting).")
        else:
            st.metric(label="Spread (10-2yr)", value=spread, help="10yr minus 2yr yield. Positive = normal curve. Negative = inverted = recession warning.")
    else:
        st.metric(label="Spread (10-2yr)", value="n/a")

# --- COMMODITY FUTURES ---
st.markdown("### Commodity Futures")
cols = st.columns(8)
show_metric(cols[0], "WTI Crude", "CL=F", "WTI crude futures. US benchmark. Key for Energy sector and inflation.")
show_metric(cols[1], "Brent Crude", "BZ=F", "Brent crude futures. Global benchmark. Slightly higher than WTI typically.")
show_metric(cols[2], "Gold", "GC=F", "Gold futures. Safe haven. Rising = risk-off, inflation hedge, or dollar weakness.")
show_metric(cols[3], "Silver", "SI=F", "Silver futures. Industrial + safe haven hybrid. Tracks gold but more volatile.")
show_metric(cols[4], "Copper", "HG=F", "Copper futures. Leading indicator of global economic health. Rising = growth.")

# --- CRYPTO ---
st.markdown("### Crypto")
cols = st.columns(8)
show_metric(cols[0], "Bitcoin", "BTC-USD", "Spot BTC. Risk-on asset. Tracks NASDAQ in risk-off, digital gold in inflation.")
show_metric(cols[1], "Ethereum", "ETH-USD", "Spot ETH. Tracks BTC but higher beta. Sensitive to DeFi and tech sentiment.")
crypto_score, crypto_rating, crypto_delta, crypto_pct = fetch_fear_greed_crypto()
with cols[2]:
    if crypto_score is not None:
        crypto_delta_str = f"{'+' if crypto_delta >= 0 else ''}{crypto_delta} ({'+' if crypto_pct >= 0 else ''}{crypto_pct}%)" if (crypto_delta is not None and crypto_pct is not None) else shorten_rating(crypto_rating)
        st.metric(label="F&G Crypto", value=crypto_score, delta=crypto_delta_str, help="Alternative.me Crypto Fear & Greed Index. Tracks Bitcoin/crypto sentiment only — not equity markets. Inputs: volatility (25%), market momentum/volume (25%), social media (15%), Bitcoin dominance (10%), Google Trends (10%). 0-25 = Extreme Fear. 25-50 = Fear. 50-75 = Greed. 75-100 = Extreme Greed. Historically below 10 = capitulation zone, strong long-term entry signal. Above 80 = overheated, historically precedes corrections.")
    else:
        st.metric(label="F&G Crypto", value="n/a", help="Alternative.me Crypto Fear & Greed Index.")

# --- CURRENCIES ---
st.markdown("### Currencies")
cols = st.columns(8)
show_metric(cols[0], "EUR/USD", "EURUSD=X", "Euro vs Dollar. Falling = dollar strength / risk-off.")
show_metric(cols[1], "USD/JPY", "JPY=X", "Dollar vs Yen. Rising = risk-on. Falling Yen = safe haven bid.")
show_metric(cols[2], "GBP/USD", "GBPUSD=X", "Pound vs Dollar. Sensitive to UK macro and global risk appetite.")
show_metric(cols[3], "USD/CNY", "USDCNY=X", "Dollar vs Yuan. Rising = yuan weakening, often signals China stress.")

time.sleep(30)
st.rerun()
