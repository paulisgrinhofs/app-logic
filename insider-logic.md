# Insider Tool Logic
Last updated: 2026-06-05

## Purpose
Scan for insider buying activity as a source of long-term investment ideas.
Not a trading tool. A research trigger — surfaces names worth investigating.

The core edge: insiders buy for one reason only — they think the stock goes up.
Legally disclosed via SEC Form 4 within 2 business days.
One of the few legal information edges available to retail investors.

---

## The Core Problem This Solves

Insider buying data is public but fragmented:
- OpenInsider shows the transactions but not the full picture
- SEC EDGAR has the footnotes but requires manual digging
- Finviz shows insider activity alongside fundamentals but no signal scoring
- Nobody combines all three with a quality filter automatically

---

## Signal Hierarchy (strongest to weakest)

1. Cluster buy — multiple insiders, same stock, within 30 days
2. CEO/CFO open market purchase — discretionary, no 10b5-1 plan
3. Large director buy — meaningful $ relative to existing position
4. Single officer buy — $500K+
5. Director buy — significant % ownership change

Cluster buys are the strongest signal because coordination would be illegal.
Independent convergence by multiple insiders implies genuine conviction.

---

## What Makes a Signal Strong

- Role: CEO/CFO stronger than Director, Director stronger than VP
- Absolute value: larger is more meaningful
- % ownership change: buying 20% more of your position means more than buying 1%
- No 10b5-1 plan: discretionary purchase beats pre-scheduled sale plan
- Post-selloff context: buying after stock down 30-50% is more meaningful than buying near highs
- Transaction code P: open market purchase only — ignore F (tax), M (option exercise), A (grant)
- Filed quickly: same-day or next-day filing sometimes signals urgency

## What Reduces Signal Quality

- 10b5-1 plan confirmed in footnotes — pre-scheduled, not discretionary
- RSU vesting or option exercise — compensation, not conviction
- Same insider sold recently — contradicts the buy
- Micro cap / illiquid stock — hard to exit
- Closed-end fund insiders buying their own fund — different dynamic

---

## Data Sources

| Source | What it provides | Access | Cost |
|--------|-----------------|--------|------|
| OpenInsider | Cluster buys, scored lists, filters | Scrape HTML | Free |
| SEC EDGAR | Raw Form 4, footnotes, ownership structure | Official API | Free |
| yfinance | Fundamentals, price history | Python library | Free |
| Finviz | Fundamentals + chart + insider activity together | Web | Free/paid |

### Key OpenInsider URLs
- Cluster buys: openinsider.com/latest-cluster-buys
- CEO/CFO buys $25K+: openinsider.com/latest-ceo-cfo-purchases-25k
- Large single buys: openinsider.com/insider-purchases

### SEC EDGAR Form 4 lookup
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=TICKER&type=4&count=10

---

## What to Verify in Raw Form 4

1. Transaction code — P = open market purchase (signal), anything else = lower quality
2. 10b5-1 checkbox at top of form — if ticked, pre-planned sale
3. Footnotes (Explanation of Responses section) — most important
   - Does it mention "Rule 10b5-1 trading plan"? If yes — reduces signal
   - Price range — weighted average or single price?
   - Fund vehicle vs personal cash — fund buy slightly weaker than personal
4. Direct vs indirect ownership — personal holding vs fund/trust
5. Ownership structure — how shares are split across entities

---

## OpenInsider vs Finviz vs Raw SEC

| | Finviz | OpenInsider | Raw SEC Form 4 |
|---|--------|-------------|----------------|
| Basic transaction data | ✅ | ✅ | ✅ |
| Cluster buy flag | ❌ | ✅ | ❌ |
| % ownership change | ❌ | ✅ | ✅ |
| Fundamentals alongside | ✅ | ❌ | ❌ |
| Chart alongside | ✅ | ❌ | ❌ |
| Footnotes / 10b5-1 | ❌ | ❌ | ✅ |
| Direct vs indirect | ❌ | ❌ | ✅ |
| Price range detail | ❌ | ❌ | ✅ |
| Free | Partial | Fully free | Fully free |

---

## Daily Scan Logic

Two scans, not one:

Scan 1 — OpenInsider cluster buys page
- Multiple insiders, same stock, recent window
- Filter: exclude closed-end funds, stocks under $5

Scan 2 — Large single buys
- Min value $500K+
- Role: Officer or Director only
- Transaction code P only
- % ownership change 10%+

Combined gives 5-10 genuinely interesting names per week.

---

## Workflow Per Interesting Name

1. OpenInsider — spot the signal
2. Finviz — check fundamentals, chart, analyst ratings, context
3. SEC EDGAR Form 4 — verify footnotes, confirm no 10b5-1 plan
4. Decision: research further or pass

---

## Exit Signal Framework

Enter on insider buy signal. Exit when thesis breaks — not on calendar.

### Checklist — review each quarter
1. Is insider buy thesis still intact?
2. Are fundamentals stable or improving?
3. Is guidance intact?
4. Any new insider selling by same or other insiders?
5. Is stock still below fair value?

3+ negative answers = exit regardless of price.

### Price-based exits
- Target: analyst consensus or Morningstar fair value reached
- Stop loss: -10% from entry if no new insider buying appears

---

## Relationship to Macro Tool

Separate tools, separate logic. No direct connection.
Insider tool = investment ideas, weeks to months timeframe.
Macro tool = daily context, sector rotation, trading timeframe.
Both inform IBKR execution but independently.

---

## Open Questions
- Alert mechanism: how to get notified of new cluster buys without manual checking?
- Historical tracking: log past signals and track outcomes to validate the approach?
- TWS integration: auto-flag if insider of a stock you own starts selling?
