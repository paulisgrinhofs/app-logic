import streamlit as st
import yfinance as yf
import requests
import time
import threading

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

def fetch_ratio(t1, t2):
    try:
        d1 = yf.Ticker(t1).fast_info
        d2 = yf.Ticker(t2).fast_info
        price = round(d1['last_price'] / d2['last_price'], 4)
        prev = round(d1['previous_close'] / d2['previous_close'], 4)
        delta = round(price - prev, 4)
        pct = round((delta / prev) * 100, 2) if prev else 0
        return price, delta, pct
    except:
        return None, None, None

def _parse_fred_csv(text):
    obs = []
    for line in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        line = line.strip()
        if not line or line.startswith('DATE'):
            continue
        parts = line.split(',')
        if len(parts) >= 2 and parts[1].strip() not in ('', '.'):
            try:
                obs.append((parts[0].strip(), float(parts[1].strip())))
            except ValueError:
                continue
    return obs

FRED_API_KEY = "eb55d58a724483b7bc037fa215b29dbf"

def _fetch_fred_raw(series_id):
    try:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=asc")
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            obs = [(o['date'], float(o['value']))
                   for o in r.json().get('observations', [])
                   if o['value'] not in ('.', '')]
            return obs
    except:
        pass
    return []

def _prefetch_slow():
    """Run slow fetches in parallel threads before page renders."""
    def _fred(series_id, cache_key, mode):
        if st.session_state.get(cache_key) and time.time() - st.session_state[cache_key]['ts'] < 3600:
            return
        obs = _fetch_fred_raw(series_id)
        if not obs:
            return
        if mode == 'single':
            st.session_state[cache_key] = {'value': str(obs[-1][1]), 'date': obs[-1][0], 'ts': time.time()}
        elif mode == 'yoy' and len(obs) >= 13:
            yoy = round(((obs[-1][1] - obs[-13][1]) / obs[-13][1]) * 100, 2)
            st.session_state[cache_key] = {'value': obs[-1][1], 'yoy': yoy, 'date': obs[-1][0], 'ts': time.time()}
        elif mode == 'mom' and len(obs) >= 2:
            mom = round(obs[-1][1] - obs[-2][1], 1)
            st.session_state[cache_key] = {'value': obs[-1][1], 'mom': mom, 'date': obs[-1][0], 'ts': time.time()}

    def _zq():
        cache_key = 'zq_cache'
        if st.session_state.get(cache_key) and time.time() - st.session_state[cache_key]['ts'] < 120:
            return
        try:
            data = yf.Ticker("ZQ=F")
            price = round(data.fast_info['last_price'], 3)
            prev = round(data.fast_info['previous_close'], 3)
            st.session_state[cache_key] = {'price': price, 'prev': prev, 'ts': time.time()}
        except:
            pass

    threads = [
        threading.Thread(target=_fred, args=("ICSA", "fred_icsa", "single")),
        threading.Thread(target=_fred, args=("CPIAUCSL", "fred_cpi", "yoy")),
        threading.Thread(target=_fred, args=("PAYEMS", "fred_nfp", "mom")),
        threading.Thread(target=_zq),
    ]
    for t in threads:
        t.daemon = True
        t.start()
    for t in threads:
        t.join(timeout=10)

_prefetch_slow()

def fetch_fred(series_id, cache_key):
    cache = st.session_state.get(cache_key)
    if cache and time.time() - cache['ts'] < 3600:
        return cache['value'], cache['date'], None
    obs = _fetch_fred_raw(series_id)
    if obs:
        value, date = str(obs[-1][1]), obs[-1][0]
        st.session_state[cache_key] = {'value': value, 'date': date, 'ts': time.time()}
        return value, date, None
    return None, None, None

def fetch_fred_yoy(series_id, cache_key):
    cache = st.session_state.get(cache_key)
    if cache and time.time() - cache['ts'] < 3600:
        return cache['value'], cache['yoy'], cache['date']
    obs = _fetch_fred_raw(series_id)
    if len(obs) >= 13:
        current_val, current_date = obs[-1][1], obs[-1][0]
        yoy = round(((current_val - obs[-13][1]) / obs[-13][1]) * 100, 2)
        st.session_state[cache_key] = {'value': current_val, 'yoy': yoy, 'date': current_date, 'ts': time.time()}
        return current_val, yoy, current_date
    return None, None, None

def fetch_fred_mom(series_id, cache_key):
    cache = st.session_state.get(cache_key)
    if cache and time.time() - cache['ts'] < 3600:
        return cache['value'], cache['mom'], cache['date']
    obs = _fetch_fred_raw(series_id)
    if len(obs) >= 2:
        current_val, current_date = obs[-1][1], obs[-1][0]
        mom = round(current_val - obs[-2][1], 1)
        st.session_state[cache_key] = {'value': current_val, 'mom': mom, 'date': current_date, 'ts': time.time()}
        return current_val, mom, current_date
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
        data = yf.Ticker("^PCCR").history(period="2d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
    except:
        pass
    return None

def fetch_fear_greed_cnn():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        url = "https://feargreedchart.com/api/?action=all"
        r = requests.get(url, timeout=5, headers=headers)
        data = r.json()
        score = data['fear_greed']['score']
        rating = data['fear_greed']['rating']
        return score, rating
    except:
        return None, None

def fetch_fear_greed_crypto():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=5)
        data = r.json()
        score = int(data['data'][0]['value'])
        rating = data['data'][0]['value_classification']
        return score, rating
    except:
        return None, None

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

pc = fetch_put_call()
with cols[2]:
    if pc is not None:
        st.metric(label="Put/Call (PCCR)", value=pc, help="CBOE Total Put/Call Ratio. Above 1.0 = more puts = bearish hedging. Below 0.7 = complacency. Contrarian: extreme readings often mark turning points.")
    else:
        st.metric(label="Put/Call (PCCR)", value="n/a", help="CBOE Total Put/Call Ratio.")

cnn_score, cnn_rating = fetch_fear_greed_cnn()
with cols[3]:
    if cnn_score:
        st.metric(label="F&G (Stocks)", value=f"{cnn_score} — {cnn_rating}", help="CNN Fear & Greed Index (equity markets). 0-25 = Extreme Fear. 25-45 = Fear. 45-55 = Neutral. 55-75 = Greed. 75-100 = Extreme Greed.")
    else:
        st.metric(label="F&G (Stocks)", value="n/a", help="CNN Fear & Greed Index for equity markets.")

crypto_score, crypto_rating = fetch_fear_greed_crypto()
with cols[4]:
    if crypto_score:
        st.metric(label="F&G (Crypto)", value=f"{crypto_score} — {crypto_rating}", help="Alternative.me Crypto Fear & Greed Index. Tracks Bitcoin/crypto sentiment only — not equity markets.")
    else:
        st.metric(label="F&G (Crypto)", value="n/a", help="Alternative.me Crypto Fear & Greed Index.")

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
with cols[4]:
    if p10 and p2:
        spread = round(p10 - p2, 2)
        st.metric(label="Spread (10-2yr)", value=spread, help="Positive = normal curve. Negative = inverted = recession warning.")
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

# --- CURRENCIES ---
st.markdown("### Currencies")
cols = st.columns(8)
show_metric(cols[0], "EUR/USD", "EURUSD=X", "Euro vs Dollar. Falling = dollar strength / risk-off.")
show_metric(cols[1], "USD/JPY", "JPY=X", "Dollar vs Yen. Rising = risk-on. Falling Yen = safe haven bid.")
show_metric(cols[2], "GBP/USD", "GBPUSD=X", "Pound vs Dollar. Sensitive to UK macro and global risk appetite.")
show_metric(cols[3], "USD/CNY", "USDCNY=X", "Dollar vs Yuan. Rising = yuan weakening, often signals China stress.")

time.sleep(30)
st.rerun()
