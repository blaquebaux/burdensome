#!/usr/bin/python3
# =============================================================================
# _burdensome_common.py — shared helpers for Blaque Baux BURDENSOME (catastrophe / reinsurance risk premium).
# Alpaca SIP daily bars (adjustment=all → total return); env keys. Read-only.
#
# The cat/reinsurance premium: you are paid to BEAR tail risk (hurricanes, quakes). BURDENSOME tests Kareem's null —
# is this "pennies in front of a steamroller," and is its return profile MATHEMATICALLY INDISTINGUISHABLE from selling
# OTM puts (bankroll/brace)? No liquid cat-bond/ILS ETF has history, so we proxy the premium with a basket of
# reinsurance / specialty-insurer equities (RNR, EG, ACGL, RLI, AXS, WRB, MKL, RGA). The decisive test is a
# decomposition: regress the basket on SPY (equity beta) AND on PUTW (the short-put profile) — if the cat premium is
# just vol-selling, PUTW explains it; if a large residual survives, it's a DISTINCT specialty premium (underwriting
# pricing cycle + cat tail + investment income), not a repackaged short put. Cat years (2017 hurricanes, 2022 Ian)
# and the 2023-25 hard market are the regime tells. Negative skew is expected either way — the question is the SOURCE.
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = [s for s in syms if s in D]; dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=float((cum/np.maximum.accumulate(cum)-1).min()), vol=r.std()*math.sqrt(252))

def skew_of(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return float('nan')
    z = (r - r.mean())/r.std(); return float(np.mean(z**3))

def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 30 else float('nan')

def regress(y, X):
    """OLS y ~ [1, X...]; returns (betas incl intercept, R²). X is a list of regressor arrays aligned to y."""
    y = np.asarray(y, float); cols = [np.ones(len(y))] + [np.asarray(x, float) for x in X]
    A = np.column_stack(cols); m = np.all(np.isfinite(A), axis=1) & np.isfinite(y)
    A, yy = A[m], y[m]
    beta, *_ = np.linalg.lstsq(A, yy, rcond=None)
    resid = yy - A @ beta; r2 = 1 - resid.var()/yy.var() if yy.var() > 0 else float('nan')
    return beta, r2
