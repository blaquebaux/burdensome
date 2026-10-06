# Blaque Baux Burdensome

**Catastrophe / reinsurance risk premium — pennies in front of a steamroller, or distinct from selling puts? A real, compensated premium — distinct from short puts, but a specialty-equity bet, not a hedge.**

The cat/reinsurance premium pays you to *bear* tail risk (hurricanes, quakes). Burdensome tests Kareem's null: is this
"pennies in front of a steamroller," and is its return profile *mathematically indistinguishable from selling OTM puts*
(`bankroll`)? No liquid cat-bond/ILS ETF has history, so the premium is proxied by a reinsurance/specialty-insurer equity
basket (RNR, EG, ACGL, RLI, AXS, WRB, MKL, RGA) — and the decisive test regresses it on SPY *and* PUTW to see whether
it's just vol-selling.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/burdensome_1_cat_premium.py   # needs Alpaca data keys in the environment
```

## The finding (real and distinct — but a specialty-equity bet, not a hedge)

[`research/burdensome_1_cat_premium.py`](research/burdensome_1_cat_premium.py) — equal-weight basket, SIP daily total return.

| | Sharpe | CAGR | maxDD | skew | corr→SPY | corr→PUTW |
|---|---|---|---|---|---|---|
| reinsurance basket | +0.71 | +14.1% | −44% | −0.67 | +0.66 | +0.60 |
| SPY | +0.82 | +13.7% | −34% | −0.66 | 1.00 | — |
| PUTW (put-write) | +0.57 | +6.8% | −28% | −1.82 | — | — |

- **A real, compensated premium with a tail** — you're paid (+14%/yr), and the steamroller is real: the basket
  *underperformed* during the 2017 hurricanes (−1% vs SPY +6%).
- **Not just selling puts (null rejected)** — equity + put-write explain only **44%** of the basket; a **56% residual**
  survives (underwriting pricing cycle + cat exposure + investment income). It is *not* a `bankroll` clone.
- **But not a diversifier** — corr to SPY **+0.66** and maxDD **−44%** (*worse* than SPY). It bundles the premium with
  full equity beta; it won't protect you in an equity crash.
- **The return is cyclical** — **+48%** in the 2023-25 hard market as reinsurance repriced post-Ian. Soft markets pay
  thin, then a mega-cat, then hard-market repricing; the standout return (and most of the residual) is this cycle, not a
  steady carry.

## Verdict

**CONDITIONAL — real, compensated, and distinct from selling puts, but a specialty-equity satellite, not a hedge.**
Kareem's "mathematically indistinguishable from OTM puts" null is rejected (56% residual beyond equity + put-write). But
temper the enthusiasm: full equity beta, a *worse* drawdown than SPY, and a cyclical return the 2023-25 hard market
carried. Size it for the tail and the cycle — the "survive a 1-in-50-year event" sizing is the whole game — not as a
low-correlation hedge. A `burdensome_2` with a real cat-bond/ILS feed would isolate the *pure* premium from equity beta.

## Status

**Research.** Honest conditional — a genuine premium confirmed and distinguished from vol-selling, with its equity beta,
cyclicality and tail stated squarely. Basket profile, cat-year and hard-market windows, SPY+PUTW decomposition, Alpaca
SIP daily total return. No live capital.
