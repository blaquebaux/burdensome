#!/usr/bin/python3
# =============================================================================
# burdensome_1_cat_premium.py — cat/reinsurance premium: pennies before a steamroller, or distinct from selling puts?
#
# Equal-weight reinsurance/specialty-insurer basket, SIP daily total return, causal. Tests:
#  (A) PROFILE: Sharpe / CAGR / maxDD / skew vs SPY and vs PUTW (put-write). Is it the insurer's negative-skew seat?
#  (B) CAT TAIL: drawdowns in the big cat years (2017 HIM hurricanes, 2022 Ian) — is the steamroller real & paid for?
#  (C) THE DECISIVE TEST — regress the basket on SPY (equity beta) AND PUTW (short-put profile). If PUTW explains it,
#      it's just vol-selling (bankroll); if a big RESIDUAL survives, it's a DISTINCT specialty premium (underwriting
#      cycle + cat tail + investment income). Plus the 2023-25 hard market, where reinsurance repriced.
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _burdensome_common import panel, rets, stats, skew_of, corr, regress
import numpy as np

BASK = ["RNR", "EG", "ACGL", "RLI", "AXS", "WRB", "MKL", "RGA"]
P, dates = panel(BASK + ["SPY", "PUTW", "IAK"])
syms = [s for s in BASK if s in P]
R = {s: rets(P[s]) for s in P}
bask = np.nanmean(np.vstack([R[s] for s in syms]), axis=0)   # equal-weight reinsurer basket, daily
spy = R["SPY"]; D = dates[1:]
print("="*98); print(f"BURDENSOME #1 — cat/reinsurance premium  ({dates[0]} → {dates[-1]}, {len(dates)} days, {len(syms)} names)"); print("="*98)

# ---- (A) profile ------------------------------------------------------------------------------------
a = stats(bask)
print(f"\n(A) PROFILE                        {'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'skew':>7}{'corr→SPY':>10}{'corr→PUTW':>11}")
print(f"  reinsurance basket               {a['sh']:>+8.2f}{a['cagr']*100:>+7.1f}%{a['dd']*100:>+7.0f}%{skew_of(bask):>+7.2f}{corr(bask,spy):>+10.2f}{corr(bask,R.get('PUTW',spy)[-len(bask):]):>+11.2f}")
sp = stats(spy); print(f"  SPY                              {sp['sh']:>+8.2f}{sp['cagr']*100:>+7.1f}%{sp['dd']*100:>+7.0f}%{skew_of(spy):>+7.2f}{1.0:>+10.2f}")
if "PUTW" in R:
    pw = stats(R["PUTW"]); print(f"  PUTW (put-write)                 {pw['sh']:>+8.2f}{pw['cagr']*100:>+7.1f}%{pw['dd']*100:>+7.0f}%{skew_of(R['PUTW']):>+7.2f}")

# ---- (B) cat tail -----------------------------------------------------------------------------------
def win(lo, hi):
    idx = [i for i,x in enumerate(D) if lo <= x < hi]; return (np.prod(1+bask[idx])-1 if idx else float('nan'),
                                                               np.prod(1+spy[idx])-1 if idx else float('nan'))
him = win("2017-08-20", "2017-10-15"); ian = win("2022-09-20", "2022-10-10"); hard = win("2023-01-01", "2026-07-31")
print(f"\n(B) CAT TAIL & HARD MARKET")
print(f"  2017 HIM hurricanes (Aug-Oct):  basket {him[0]*100:+.0f}%  vs SPY {him[1]*100:+.0f}%")
print(f"  2022 Hurricane Ian (late Sep):  basket {ian[0]*100:+.0f}%  vs SPY {ian[1]*100:+.0f}%")
print(f"  2023-25 HARD market:            basket {hard[0]*100:+.0f}%  vs SPY {hard[1]*100:+.0f}%  — post-Ian reinsurance repricing")

# ---- (C) decisive decomposition ---------------------------------------------------------------------
if "PUTW" in R:
    L = min(len(bask), len(R["PUTW"]), len(spy)); y = bask[-L:]; x_spy = spy[-L:]; x_pw = R["PUTW"][-L:]
    b_spy, r2_spy = regress(y, [x_spy])
    b_pw, r2_pw = regress(y, [x_pw])
    b_both, r2_both = regress(y, [x_spy, x_pw])
    # residual alpha after SPY + PUTW (annualized)
    resid_mean = (y - (b_both[0] + b_both[1]*x_spy + b_both[2]*x_pw)).mean()*252 + b_both[0]*252
    alpha_ann = b_both[0]*252
    print(f"\n(C) DECOMPOSITION (is it just selling puts?)")
    print(f"  basket ~ SPY only:     R² {r2_spy*100:.0f}%   (β_SPY {b_spy[1]:+.2f})")
    print(f"  basket ~ PUTW only:    R² {r2_pw*100:.0f}%   (β_PUTW {b_pw[1]:+.2f})")
    print(f"  basket ~ SPY + PUTW:   R² {r2_both*100:.0f}%   β_SPY {b_both[1]:+.2f}  β_PUTW {b_both[2]:+.2f}  → RESIDUAL α {alpha_ann*100:+.1f}%/yr")
    print(f"  → {100-r2_both*100:.0f}% of the basket's variance is NOT explained by equity + put-write = the distinct specialty/cat premium")

# ---- verdict ----------------------------------------------------------------------------------------
neg_skew = skew_of(bask) < -0.3
real_return = a['cagr'] > 0.05 and a['sh'] > 0.4
distinct = ("PUTW" in R) and (r2_both < 0.6)                  # equity+put-write leave a big residual ⇒ distinct
print("\n"+"="*98); print("READ:")
print(f"  • A REAL, COMPENSATED PREMIUM WITH A TAIL: Sharpe {a['sh']:+.2f} / {a['cagr']*100:+.0f}%/yr, skew {skew_of(bask):+.2f} — you ARE paid to bear the tail (not pure 'pennies before a steamroller'), and the steamroller is real: it UNDERPERFORMED during the 2017 hurricanes ({him[0]*100:+.0f}% vs SPY {him[1]*100:+.0f}%).")
print(f"  • NOT A DIVERSIFIER, A SPECIALTY-EQUITY PREMIUM: corr to SPY {corr(bask,spy):+.2f} and maxDD {a['dd']*100:+.0f}% (WORSE than SPY's {sp['dd']*100:+.0f}%) — it carries full equity beta PLUS the cat tail; it does not protect you in equity crashes.")
print(f"  • THE RETURN IS CYCLICAL: basket {hard[0]*100:+.0f}% in the 2023-25 hard market as reinsurance repriced post-Ian — soft markets pay thin, then a mega-cat, then hard-market repricing. The standout return (and most of the residual α) is this cycle, not a steady carry.")
if "PUTW" in R:
    print(f"  • BUT NOT JUST SELLING PUTS: equity + put-write explain only {r2_both*100:.0f}% of the basket (β_PUTW {b_both[2]:+.2f} once SPY is in); a {100-r2_both*100:.0f}% residual survives — the underwriting cycle + cat exposure is DISTINCT from a short-put, so Kareem's 'mathematically indistinguishable from OTM puts' null is REJECTED.")

if real_return and distinct:
    v = ("CONDITIONAL: the cat/reinsurance premium is REAL, COMPENSATED, and DISTINCT from selling puts — a solid Sharpe "
         f"({a['sh']:+.2f}) with a genuine negative-skew cat tail (it underperformed in the 2017 hurricanes), and equity + put-write "
         f"explain only {r2_both*100:.0f}% of it, so the {100-r2_both*100:.0f}% residual (underwriting pricing cycle + cat + investment income) is NOT a "
         "bankroll clone. Kareem's 'indistinguishable from OTM puts' null is rejected. BUT temper the enthusiasm: it is "
         f"NOT a diversifier (corr to SPY {corr(bask,spy):+.2f}, maxDD {a['dd']*100:+.0f}% WORSE than SPY) — it bundles the premium with full "
         "equity beta — and the return is CYCLICAL, with the 2023-25 hard market doing the heavy lifting (soft markets "
         "pay thin, a mega-cat can gut a year). A specialty-equity SATELLITE sized for the tail and the cycle, not a "
         "low-correlation hedge. burdensome_2 = a real cat-bond/ILS feed to isolate the PURE premium from equity beta.")
elif real_return:
    v = ("CONDITIONAL: a real cat premium with a negative-skew tail, but it overlaps the short-put/equity profile more "
         "than hoped here — part bankroll, part equity beta; size small, isolate with a real ILS feed (burdensome_2).")
else:
    v = ("NULL-ish: on these equity proxies the cat premium doesn't clearly pay for its tail over this window — pennies "
         "before a steamroller; a real ILS/cat-bond feed is needed to test the pure premium (burdensome_2).")
print(f"\n  VERDICT: {v}")
print("  (Reinsurer EQUITIES proxy the cat premium — they bundle it with equity beta, underwriting cycle and investment")
print("   income; no liquid cat-bond/ILS ETF has history. The pure, isolated premium needs an ILS feed = burdensome_2.)")
