import streamlit as st
import yfinance as yf
import requests
import time
import threading
import json
import os

_PC_PREV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pc_prev.json")

def _load_pc_prev():
    """Return yesterday's closing Put/Call score."""
    try:
        with open(_PC_PREV_FILE) as f:
            return json.load(f).get("prev_score")
    except:
        return None

def _save_pc_prev(score):
    """
    Maintain two slots: prev_score (yesterday, never overwritten during the day)
    and today_score/today_date (updated each fetch).
    At midnight rollover: today becomes prev.
    """
    try:
        today = time.strftime("%Y-%m-%d")
        data = {}
        try:
            with open(_PC_PREV_FILE) as f:
                data = json.load(f)
        except:
            pass
        # If today_date has rolled to a new day, promote today -> prev
        if data.get("today_date") and data["today_date"] != today:
            data["prev_score"] = data.get("today_score")
        # Always update today slot
        data["today_score"] = score
        data["today_date"] = today
        with open(_PC_PREV_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

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

def fmt_delta(delta, pct):
    if delta is None:
        return None
    if pct is not None:
        return f"{'+' if delta >= 0 else ''}{delta} ({'+' if pct >= 0 else ''}{pct}%)"
    return f"{'+' if delta >= 0 else ''}{delta}"

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
            return [(o['date'], float(o['value']))
                    for o in r.json().get('observations', [])
                    if o['value'] not in ('.', '')]
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

    threads = [
        threading.Thread(target=_fred, args=("ICSA", "fred_icsa", "single")),
        threading.Thread(target=_fred, args=("CPIAUCSL", "fred_cpi", "yoy")),
        threading.Thread(target=_fred, args=("PAYEMS", "fred_nfp", "mom")),
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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", timeout=5, headers=headers)
        data = r.json()
        for key in ['put_and_call_options', 'put_call_options']:
            block = data.get(key, {})
            score = block.get('score')
            if score is not None:
                score = round(float(score), 1)
                prev = _load_pc_prev()
                _save_pc_prev(score)
                delta = round(score - prev, 1) if prev is not None else None
                pct = round((delta / prev) * 100, 1) if (delta is not None and prev) else None
                return score, delta, pct
    except:
        pass
    return None, None, None

def fetch_fear_greed_cnn():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", timeout=5, headers=headers)
        data = r.json()
        fg = data['fear_and_greed']
        score = round(fg['score'], 1)
        rating = fg['rating'].replace("_", " ").title()
        prev = fg.get('previous_close')
        delta = round(score - float(prev), 1) if prev is not None else None
        pct = round((delta / float(prev)) * 100, 1) if (delta is not None and prev) else None
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
        pct = round((delta / prev) * 100, 1) if (delta is not None and prev) else None
        return score, rating, delta, pct
    except:
        return None, None, None, None

def show_metric(col, label, ticker, help_text):
    with col:
        price, delta, pct = fetch(ticker)
        if price is None:
            st.metric(label=label, value="n/a", help=help_text)
        else:
            st.metric(label=label, value=price, delta=fmt_delta(delta, pct), help=help_text)

# --- RISK SENTIMENT ---
st.markdown("### Risk Sentiment")
cols = st.columns(8)
show_metric(cols[0], "VIX", "^VIX", "Fear index. Below 15 = calm. 15-25 = caution. Above 25 = fear. Above 30 = panic.")
show_metric(cols[1], "DXY", "DX-Y.NYB", "USD index (spot). Rising = risk-off or strong US growth. Falling = risk-on.")

pc, pc_delta, pc_pct = fetch_put_call()
with cols[2]:
    if pc is not None:
        st.metric(label="Put/Call", value=pc, delta=fmt_delta(pc_delta, pc_pct), help="CNN-normalised Put/Call ratio (0-100 scale). Source: CBOE options data via CNN F&G API. Higher = more calls vs puts = bullish. Lower = more puts vs calls = bearish hedging. Contrarian: extremes often mark turning points. Change = vs previous close.")
    else:
        st.metric(label="Put/Call", value="n/a", help="Put/Call Ratio — sourced from CNN F&G API sub-components.")

cnn_score, cnn_rating, cnn_delta, cnn_pct = fetch_fear_greed_cnn()
with cols[3]:
    if cnn_score:
        cnn_delta_str = fmt_delta(cnn_delta, cnn_pct) if cnn_delta is not None else shorten_rating(cnn_rating)
        st.metric(label="F&G Stocks", value=cnn_score, delta=cnn_delta_str, help="CNN Fear & Greed Index (equity markets). Composite of 7 inputs: market momentum, stock price strength, breadth, put/call options, junk bond demand, market volatility, safe haven demand. 0-25 = Extreme Fear. 25-45 = Fear. 45-55 = Neutral. 55-75 = Greed. 75-100 = Extreme Greed. Historically below 25 = long-term value buyers step in. Above 75 = market most vulnerable to pullback. Change = vs previous close.")
    else:
        st.metric(label="F&G Stocks", value="n/a", help="CNN Fear & Greed Index for equity markets.")

# --- EQUITY FUTURES & INDICES ---
st.markdown("### Equity Futures & Indices")
cols = st.columns(8)
show_metric(cols[0], "S&P 500", "^GSPC", "S&P 500 cash index (^GSPC). % change vs yesterday's official 4pm close — matches what Bloomberg/Finviz report. Goes stale outside market hours.")
show_metric(cols[1], "NASDAQ 100", "^NDX", "NASDAQ 100 cash index (^NDX). % change vs yesterday's official close. Futures (NQ=F) were used previously but their % change was misleading — measured vs futures settlement, not cash close.")
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
            st.metric(label="Spread (10-2yr)", value=spread, delta=fmt_delta(spread_delta, spread_pct), help="10yr minus 2yr yield. Positive = normal curve. Negative = inverted = recession warning. Narrowing = curve flattening (tightening conditions). Widening = steepening (growth expectations rising or Fed cutting).")
        else:
            st.metric(label="Spread (10-2yr)", value=spread, help="10yr minus 2yr yield. Positive = normal curve. Negative = inverted = recession warning.")
    else:
        st.metric(label="Spread (10-2yr)", value="n/a")

# --- STRESS & CREDIT ---
st.markdown("### Stress & Credit")
cols = st.columns(8)
show_metric(cols[0], "MOVE Index", "^MOVE",
    "Bond market volatility (Treasury VIX equivalent). Leads equity vol — rising MOVE with flat VIX = bond market pricing stress equities haven't woken up to yet. "
    "Normal: <80. Elevated: 80–100. Stress: 100–150. Crisis: >150. (2020 COVID peak: ~160. 2023 banking crisis: ~140).")
show_metric(cols[1], "HYG", "HYG",
    "iShares high-yield corporate bond ETF. Falling price = credit stress, default risk rising, risk-off. Leads equity selloffs by days. "
    "Normal range: $76–$82. Stress: $70–$76. Crisis: <$70. (2020 COVID low: ~$68. 2022 rate shock low: ~$70).")
show_metric(cols[2], "JNK", "JNK",
    "SPDR high-yield bond ETF. Similar to HYG but slightly different composition. Use as confirmation — divergence from HYG is rare and significant. "
    "Normal range: $92–$100. Stress: $85–$92. Crisis: <$85.")
hyg_tlt, hyg_tlt_delta, hyg_tlt_pct = fetch_ratio("HYG", "TLT")
with cols[3]:
    if hyg_tlt is not None:
        st.metric(label="HYG/TLT", value=hyg_tlt, delta=fmt_delta(hyg_tlt_delta, hyg_tlt_pct),
            help="Ratio: high-yield bonds (HYG) ÷ long-term Treasuries (TLT). More sensitive to credit stress than raw HYG price. "
                 "Rising = risk appetite, investors in credit over safety. Falling = flight to safety, systemic stress. "
                 "Direction matters more than absolute level. Sustained decline = credit market warning ahead of equities.")
    else:
        st.metric(label="HYG/TLT", value="n/a", help="HYG/TLT ratio — credit vs safe haven demand.")
show_metric(cols[4], "TLT", "TLT",
    "iShares 20yr+ Treasury bond ETF. Inverse of long rates — rising TLT = rates falling = safety bid or recession fears. Falling TLT = rates rising = inflation/growth. "
    "Normal range varies with rate cycle. Key: watch direction relative to equities. TLT up + equities down = classic risk-off. TLT down + equities up = reflation trade.")

# --- BREADTH ---
st.markdown("### Breadth")
cols = st.columns(8)
show_metric(cols[0], "RSP", "RSP",
    "Invesco equal-weight S&P 500 ETF. Each of 500 stocks has identical ~0.2% weight. "
    "Rising = broad market health. Use alongside SPY to assess participation.")
show_metric(cols[1], "SPY", "SPY",
    "SPDR S&P 500 ETF, market-cap weighted. Top 10 stocks = ~35% of index. "
    "Can rise even if most stocks are flat or falling if mega-caps lead.")
rsp_spy, rsp_spy_delta, rsp_spy_pct = fetch_ratio("RSP", "SPY")
with cols[2]:
    if rsp_spy is not None:
        st.metric(label="RSP/SPY", value=rsp_spy, delta=fmt_delta(rsp_spy_delta, rsp_spy_pct),
            help="Breadth ratio: equal-weight ÷ cap-weight S&P 500. "
                 "Rising = rally is broad, most stocks participating = healthy. "
                 "Falling = rally driven by few mega-caps, narrow and fragile — historically precedes broader weakness. "
                 "Typical range: 0.26–0.32. Multi-year low ~0.24 (2023 AI concentration peak). "
                 "Key signal: SPY up + RSP/SPY falling = do not trust the index move.")
    else:
        st.metric(label="RSP/SPY", value="n/a", help="RSP/SPY breadth ratio.")

# --- MACRO DATA ---
st.markdown("### Macro Data")
cols = st.columns(8)

# Fed Funds implied rate — ZQ=F fetched inline (fast_info, ~0.3s)
zq_price, zq_prev = None, None
try:
    fi = yf.Ticker("ZQ=F").fast_info
    p = fi['last_price']
    pv = fi['previous_close']
    if p is not None and pv is not None:
        zq_price = round(float(p), 3)
        zq_prev = round(float(pv), 3)
except:
    pass
with cols[0]:
    if zq_price is not None:
        implied_rate = round(100 - zq_price, 3)
        implied_prev = round(100 - zq_prev, 3) if zq_prev is not None else None
        rate_delta = round(implied_rate - implied_prev, 3) if implied_prev is not None else None
        rate_pct = round((rate_delta / implied_prev) * 100, 2) if (rate_delta and implied_prev) else None
        st.metric(label="Fed Funds Implied", value=f"{implied_rate}%", delta=fmt_delta(rate_delta, rate_pct),
            help="Market-implied Fed Funds rate from ZQ=F (30-day futures). Formula: 100 minus futures price. "
                 "Compare to current Fed Funds target (set by FOMC). Gap = market pricing in cuts or hikes. "
                 "Overnight shift in implied rate = most direct signal that macro catalyst changed rate expectations. "
                 "Normal: tracks Fed target closely. Diverging lower = market pricing cuts = risk-on signal.")
    else:
        st.metric(label="Fed Funds Implied", value="n/a", help="Implied Fed Funds rate from ZQ=F futures.")

# Jobless Claims — FRED series ICSA (weekly, Thursdays)
claims_val, claims_date, _ = fetch_fred("ICSA", "fred_icsa")
with cols[1]:
    if claims_val:
        st.metric(label="Jobless Claims", value=f"{int(float(claims_val)):,}", delta=claims_date, delta_color="off",
            help=f"Weekly initial jobless claims (FRED: ICSA). Released every Thursday 8:30am ET. "
                 f"Healthy: <220k. Normal: 220–260k. Elevated: 260–300k. Concern: 300–400k. Recession signal: >400k sustained. "
                 f"(2020 COVID peak: 6.1M. 2023 normal: ~220k). Leading indicator — moves before monthly NFP. Last release: {claims_date}.")
    else:
        st.metric(label="Jobless Claims", value="n/a", help="Weekly initial jobless claims from FRED (ICSA).")

# CPI YoY — FRED series CPIAUCSL (monthly), calculated from 13 months of data
cpi_val, cpi_yoy, cpi_date = fetch_fred_yoy("CPIAUCSL", "fred_cpi")
with cols[2]:
    if cpi_yoy is not None:
        yoy_str = f"{'+' if cpi_yoy >= 0 else ''}{cpi_yoy}% YoY"
        st.metric(label="CPI YoY", value=f"{cpi_yoy}%", delta=cpi_date, delta_color="off",
            help=f"CPI year-on-year % change (FRED: CPIAUCSL). Calculated from current vs 12 months prior. "
                 f"Fed target: ~2%. Cooling: 2–3%. Hot: 3–5%. Crisis: >6% (2022 peak: 9.1%). Deflation risk: <0%. "
                 f"Last release: {cpi_date}.")
    else:
        st.metric(label="CPI YoY", value="n/a", help="CPI YoY % change from FRED (CPIAUCSL).")

# NFP MoM — FRED series PAYEMS (monthly, first Friday)
nfp_val, nfp_mom, nfp_date = fetch_fred_mom("PAYEMS", "fred_nfp")
with cols[3]:
    if nfp_mom is not None:
        mom_str = f"{'+' if nfp_mom >= 0 else ''}{int(nfp_mom):,}k"
        st.metric(label="NFP MoM", value=mom_str, delta=nfp_date, delta_color="off",
            help=f"Non-Farm Payrolls month-on-month change (FRED: PAYEMS, thousands). Released first Friday each month. "
                 f"Strong: >+250k. Healthy: +150–250k. Weak: +50–150k. Stalling: <+50k. Recession: negative. "
                 f"(2020 COVID: -20M in 2 months. 2022–23 avg: ~+250k/month). Last release: {nfp_date}.")
    else:
        st.metric(label="NFP MoM", value="n/a", help="Non-Farm Payrolls MoM change from FRED (PAYEMS).")

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
        crypto_delta_str = fmt_delta(crypto_delta, crypto_pct) if crypto_delta is not None else shorten_rating(crypto_rating)
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

time.sleep(120)
st.rerun()
