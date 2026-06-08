import streamlit as st
import yfinance as yf
import time

st.title("Macro Dashboard")
st.markdown("## Market Inputs")

tickers = {
    "VIX": {
        "ticker": "^VIX",
        "help": "Fear index. Below 15 = calm. 15-25 = caution. Above 25 = fear. Above 30 = panic."
    },
    "S&P 500 Futures": {
        "ticker": "ES=F",
        "help": "Pre-market S&P 500 direction. Positive = risk-on open expected."
    },
    "NASDAQ Futures": {
        "ticker": "NQ=F",
        "help": "Pre-market tech direction. Leads growth/risk sentiment."
    },
    "10yr Yield": {
        "ticker": "^TNX",
        "help": "10-year Treasury yield. Rising = growth/inflation expectations up. Falling = safety bid or recession fear."
    },
    "2yr Yield": {
        "ticker": "^IRX",
        "help": "2-year Treasury yield. Watch spread vs 10yr. 2yr > 10yr = inverted curve = recession signal."
    },
    "Dollar Index": {
        "ticker": "DX=F",
        "help": "USD strength. Rising = risk-off or strong US growth. Falling = risk-on, weak dollar benefits commodities and EM."
    },
    "Oil WTI": {
        "ticker": "CL=F",
        "help": "West Texas crude price. Key driver for Energy sector. Also signals inflation expectations."
    },
    "Put/Call Ratio": {
        "ticker": "^CPC",
        "help": "Options sentiment. Below 0.7 = complacency. Above 1.0 = fear. Contrarian indicator at extremes."
    },
}

for name, info in tickers.items():
    try:
        data = yf.Ticker(info["ticker"])
        price = round(data.fast_info['last_price'], 2)
        st.metric(label=name, value=price, help=info["help"])
    except:
        st.metric(label=name, value="unavailable", help=info["help"])

time.sleep(30)
st.rerun()
