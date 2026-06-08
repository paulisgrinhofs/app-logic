import streamlit as st
import yfinance as yf

st.title("Macro Dashboard")

# --- MARKET INPUTS ---
# Logic ref: macro-logic.md → Inputs → Price/Market

st.markdown("## Market Inputs")

tickers = {
    "VIX": "^VIX",
    "S&P 500 Futures": "ES=F",
    "NASDAQ Futures": "NQ=F",
    "10yr Yield": "^TNX",
    "2yr Yield": "^IRX",
    "Dollar Index": "DX=F",
    "Oil WTI": "CL=F",
    "Put/Call Ratio": "^CPC",
}

for name, ticker in tickers.items():
    try:
        data = yf.Ticker(ticker)
        price = round(data.fast_info['last_price'], 2)
        st.markdown(f"### {name} {price}")
    except Exception as e:
        st.markdown(f"### {name} — unavailable")
