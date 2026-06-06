
1. Long signal — what we've been doing
Spot insider buying as a catalyst for going long. Works best with cluster buys, C-suite involvement, large % ownership change, post-selloff context. The classic retail use case.

2. Short signal — the opposite
Heavy insider selling, especially discretionary (no 10b5-1 plan), multiple insiders selling simultaneously, CEO/CFO selling near highs. Not as clean as buy signals but combined with weak fundamentals or high valuation it strengthens a short thesis. Exactly what we saw with RBRK today — CTO dumping $18M before earnings.

3. Earnings trade confirmation
Before taking a position ahead of earnings, check if insiders bought or sold recently. If insiders bought heavily 2-3 months ago — they likely knew the quarter was strong. If they sold — be cautious. Used as a filter layer on top of options plays.

4. Sector rotation signals
When multiple insiders across different companies in the same sector all start buying around the same time — it signals the whole sector may be bottoming. Example: if 6 different energy company CEOs all buy in the same month, energy may be turning before the market prices it in.

5. M&A / takeover detection
Sometimes insiders buy heavily just before an acquisition announcement. Technically illegal if they know — but it happens. Unusual cluster buys in small/mid cap companies with no obvious catalyst sometimes precede takeover bids by weeks. Controversial strategy but traders watch for it.

6. Confirming your existing thesis
You've done fundamental analysis, you like a stock, but you're not sure about timing. Checking if insiders are buying confirms you're not missing something negative they know about. Absence of selling is also reassuring.

7. Screening for unknown names
Many traders use OpenInsider purely as a discovery tool — they have no existing view, they just scan for large conviction buys and then go research those companies from scratch. Completely bottom-up — let insider behavior lead you to stocks you'd never have found otherwise. AVBC with 8 insiders buying — most people have never heard of it.

8. Tracking activist investors and 10% owners
When a 10% owner — often a hedge fund or activist — starts buying more, it can signal they're building toward a campaign to push management for changes, buybacks, or a sale. Different from regular insider buying but shows up in the same Form 4 feed.

9. Insider selling as exit signal for existing holders
If you already own a stock and suddenly see the CEO start selling large amounts — even via 10b5-1 — it's a prompt to review your thesis. Not an automatic sell but a flag to pay attention.

10. Academic / quant research
Quantitative funds backtest insider buying data systematically across thousands of stocks over years to find which specific combinations of signals — role, size, % ownership, cluster count, time since last sale — generate the most reliable alpha. OpenInsider's historical data is used for exactly this kind of backtesting.
    
Claude responded: Order book depth = a live list of all pending buy and sell orders for a stock at every price level.
Order book depth = a live list of all pending buy and sell orders for a stock at every price level.
  Practical example:
You're watching HOOD at $83. Order book shows 500,000 shares for sale at $84. That's a significant wall — price probably stalls there unless a big buyer absorbs it all. Useful for timing entries and exits.


For your app — practical market direction tab:


    "VIX":    yf.Ticker("^VIX"),      # fear
    "SP500":  yf.Ticker("ES=F"),      # S&P futures
    "NASDAQ": yf.Ticker("NQ=F"),      # tech direction
    "PUT_CALL": yf.Ticker("^CPC"),    # put/call ratio
    "10YR":   yf.Ticker("^TNX"),      # bonds/rates
    "DXY":    yf.Ticker("DX=F"),      # dollar strength
}
Six numbers gives you a complete macro picture — fear level, equity direction, rates, dollar. All free, all from yfinance, updates in real time.
Combined with your insider scanner — you'd know both the macro environment AND what smart money inside specific companies is doing simultaneously.
  Ranked overall for a serious investor/trader:
1. 10-K — foundation, read once a year deeply
2. 10-Q — quarterly health check
3. Form 4 — real-time signal, check regularly
4. 8-K — news/events as they happen
5. DEF 14A — management alignment check
6. S-1 — only relevant for new IPOs but incredibly rich with detail since it's the first full disclosure
   1. Technical triggers
* Breakout — stock breaks above resistance level it's been stuck at for weeks/months
* Moving average crossover — 50-day crosses above 200-day (golden cross) = bullish signal
* RSI oversold — below 30 means stock potentially oversold, bounce candidate
* Volume spike — unusual volume without news often precedes a move
* Chart patterns — cup and handle, head and shoulders, flags

2. Fundamental triggers
* Earnings beat — company beats estimates significantly, guidance raised
* Revenue acceleration — growth rate speeding up quarter over quarter
* Margin expansion — company becoming more profitable over time
* Free cash flow inflection — company turns cash flow positive for first time
* Debt paydown — balance sheet improving faster than expected

3. Flow triggers
* Unusual options activity — large call buying before a move, what Unusual Whales tracks
* Dark pool prints — large block trades executed off-exchange, institutional accumulation
* Short interest rising or falling — high short interest + good news = short squeeze
* 13F filings — big hedge funds disclose positions quarterly, see what smart money bought
* Insider buying — what we've been discussing

4. Event-driven triggers
* Earnings — most common, predictable timing, options market prices the move in advance
* FDA approvals — huge for biotech, binary outcome
* M&A rumors or announcements — target company spikes immediately
* Spin-offs — parent company separates a division, often both trade cheap initially
* Share buyback announcements — company buying own stock, reduces float
* Dividend initiation — signals management confidence in cash flow

5. Macro triggers
* Fed rate decisions — rate cuts bullish for growth stocks, real estate, bonds
* CPI/inflation data — below expectations = rally, above = selloff
* Jobs report — strong employment = economy healthy but may delay rate cuts
* Dollar movement — weak dollar bullish for commodities, multinationals
* Oil price — energy sector obviously, but also inflation expectations

6. Sentiment/contrarian triggers
* Extreme fear — VIX spike above 30, CNN Fear & Greed index at extremes = buying opportunity historically
* Analyst downgrades — counterintuitively, mass downgrades after a selloff often mark the bottom
* Magazine cover indicator — when mainstream media puts a stock on the cover, the move is usually over
* Reddit/social media surge — can create short-term momentum, dangerous to hold
* 52-week lows list — value hunters scan for quality companies at depressed prices

7. Structural/thematic triggers
* Sector rotation — money moving from tech to energy, or growth to value, creates winners and losers
* Index inclusion — stock added to S&P 500 forces index funds to buy, mechanical demand
* Index exclusion — opposite, forced selling
* Regulatory change — new law benefits or hurts specific industry
* Technological disruption — new technology makes old business model obsolete or creates new one

8. Quantitative/systematic triggers
* Factor models — momentum, value, quality, low volatility factors systematically screened
* Mean reversion — stock that moved 3+ standard deviations from mean statistically likely to revert
* Earnings revision momentum — analysts consistently raising estimates = strong buy signal
* Price to sales at historical lows — purely mechanical valuation screen


This is actually fascinating mechanics. NYSE and Nasdaq publish what they call "Order Imbalance Indicators" — public data feeds showing how much buy vs sell pressure is queued for the close.

3:50pm — first imbalance publication
Every few seconds after — updates as more orders queue up
Shows: net imbalance, indicative clearing price, paired shares
