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
        "help": "S&P 500 futures contract (ES=F). Tracks the cash index closely but trades 24/7. More useful than cash index pre-market."
    },
    "NASDAQ Futures": {
        "ticker": "NQ=F",
        "help": "NASDAQ 100 futures contract. Leads tech/growth sentiment pre-market."
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
        "ticker": "DX-Y.NYB",
        "help": "USD strength. Rising = risk-off or strong US growth. Falling = risk-on, weak dollar benefits commodities and EM."
    },
    "Oil WTI": {
        "ticker": "CL=F",
        "help": "West Texas crude price. Key driver for Energy sector. Also signals inflation expectations."
    },
    "Put/Call Ratio": {
        "ticker": "^PCCE",
        "help": "Equity put/call ratio. Below 0.7 = complacency. Above 1.0 = fear. Contrarian indicator at extremes."
    },
}

for name, info in tickers.items():
    try:
        data = yf.Ticker(info["ticker"])
        price = round(data.fast_info['last_price'], 2)
        prev_close = round(data.fast_info['previous_close'], 2)
        delta = round(price - prev_close, 2)
        pct = round((delta / prev_close) * 100, 2) if prev_close else None

        # show % change for index futures
        if info["ticker"] in ["ES=F", "NQ=F"]:
            label = f"{name}  ({'+' if pct >= 0 else ''}{pct}%)"
        else:
            label = name

        st.metric(label=label, value=price, delta=delta, help=info["help"])
    except:
        st.metric(label=name, value="unavailable", help=info["help"])

time.sleep(30)
st.rerun()
