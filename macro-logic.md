# Macro Tool Logic
Last updated: 2026-06-05

## Purpose
One tool. One daily output. Before market open.

Automates the daily macro context check — pulling together what an investor needs to understand before markets open. A context layer that answers:
- Did anything change overnight?
- Is today's sector flow real or mechanical?
- Risk-on or risk-off?

---

## The Core Problem This Solves

Every tool gives you either:
- Raw data (MacroMicro, Bloomberg) — too much, you do the synthesis
- Buy/sell signals — black box, no understanding of why
- Charts (Finviz, TradingView) — tells you what happened, not why

The gap: nobody pulls it together into "here's what happened overnight,
here's what it means for today's sector flow, here's whether the move
you're seeing is real or mechanical."

---

## The Key Insight (from observation)

Two completely different mechanics produce identical price action on a heat map.

The trigger is a counter-move day within a short-term (3-5 day) trend — e.g. a red day in a sector that has been trending up, or a green day in a sector trending down.

### Mechanical Rebalancing
- Sector moves in one direction for 3-5 days → funds rebalance allocation → counter-move day
- No macro catalyst overnight
- Counter-move is noise within the existing trend
- Response: FADE the move

### Trend Reversal
- Macro catalyst present overnight
- Counter-move is the start of a new short-term direction
- Response: FOLLOW the move

The morning brief answers: is today's counter-move a reversal or rebalancing?

---

## The Three Core Questions

Everything reduces to these:

1. Did macro context shift overnight? (yes/no + what changed)
2. Is today's counter-move a reversal or rebalancing? (per sector)
3. Risk-on or risk-off today? (with confidence level)

---

## Inputs (all automated, no manual feeding)

### Price/Market (Yahoo Finance — free, real-time)
- VIX — fear level
- S&P 500 futures (ES=F)
- NASDAQ futures (NQ=F)
- 10yr yield (^TNX)
- **[NEW]** 2yr yield — for spread vs 10yr
- Dollar index (DX=F)
- **[NEW]** Oil WTI (CL=F)
- Put/call ratio (^CPC)
- All 11 GICS sector ETFs — pre-market move + volume vs 20-day avg

### Macro Data (FRED API — free, on release days)
- NFP (jobs)
- ADP (private payrolls)
- CPI (inflation)
- PCE (Fed preferred inflation)
- ISM manufacturing + services
- Retail sales

### News/Narrative (NewsAPI/RSS — free tier)
- Fed speeches and minutes (Fed RSS)
- Top financial headlines — Reuters, FT, WSJ
- Earnings call tone — on earnings days

### What is NOT included (yet)
- Dark pool prints — expensive, needs Bloomberg/Refinitiv
- Full article text — headlines give 80% of signal
- Individual stock news — sector level only

---

## Sector Coverage — All 11 GICS

| Sector | ETF | Key macro driver |
|--------|-----|-----------------|
| Technology | XLK | Rates (valuation) + AI capex |
| Financials | XLF | Rates (margins) + growth |
| Healthcare | XLV | Defensive, low cycle sensitivity |
| Energy | XLE | Oil price + geopolitics |
| Consumer Discretionary | XLY | Consumer health + rates |
| Consumer Staples | XLP | Defensive bond proxy |
| Industrials | XLI | US macro + capex cycle |
| Materials | XLB | China + commodities + dollar |
| Real Estate | XLRE | Most rate-sensitive |
| Utilities | XLU | Rate-sensitive bond proxy |
| Communication Services | XLC | Mixed growth + defensive |

### Regional ETFs
| Region | ETF |
|--------|-----|
| Europe | EFA / VGK |
| China | FXI / MCHI |
| Emerging Markets | EEM / VWO |
| Japan | EWJ |

---

## Output Format

MORNING BRIEF — [Date]

MACRO CONTEXT SHIFT: YES / NO
  — [What changed overnight, one line each]

REGIME: [Label]
CONFIDENCE: High / Medium / Low
RISK-ON / RISK-OFF: [Direction]

SECTOR FLOW:
  Energy      → [Structural / Mechanical / Mixed] — [one line reason]
  Utilities   → [Structural / Mechanical / Mixed] — [one line reason]
  [all 11 sectors]

FADE OR FOLLOW:
  [Sector] selling today → FADE / FOLLOW — [reason]

WATCH TODAY:
  [1-3 specific variables that would change the posture]

---

## Classification Logic (skeleton)

What feeds the rebalancing vs reversal call per sector:

- Short-term trend direction (last 3-5 daily candles per sector ETF)
- Counter-move detected today (yes/no)
- Macro catalyst present overnight (yes/no — from news/FRED layer)
- Volume on today's move vs 20-day average

Decision rules TBD — this section to be expanded.

---

## Open Questions
- Update frequency: 6am daily only, or refresh intraday on major news?
- Regional ETF coverage: include from day one or add later?
- Overlap with insider tool: shared macro context layer or fully separate?
- How to handle conflicting signals — average or flag explicitly?
