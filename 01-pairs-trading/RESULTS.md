# Pairs Trading — Results and Write-up

Universe: `XOM CVX COP JPM BAC WFC GS MS ICE CME V MA` (12 tickers, 66 pairs)
Formation window: 2018-01-01 → 2021-12-31 (pair selection only)
Trading window: 2022-01-01 → 2024-12-31 (out of sample)
Signal: 60-day rolling z-score, entry |z| = 2.0, exit |z| = 0.5
Costs: 5 bps per unit of position change, charged on both legs
Risk-free rate assumed 0.

All 20 tests pass (`pytest -q`).

---

## Headline result

`run_backtest.py` picks the lowest-p-value pair from the formation window and trades it:

| Pair | beta | Total return | Sharpe | Max drawdown | Round trips |
|---|---|---|---|---|---|
| CVX / WFC | 1.03 | +3.40% | 0.17 | −15.1% | 14 |

Over three years, net of costs. That is a bad strategy — a Sharpe of 0.17 with a 15% drawdown
is not something anyone would fund. The interesting part is *why*, and the answer is visible in
the rest of the scan.

## Every pair that passed, traded out of sample

| Pair | In-sample p | Out-of-sample p | Return | Sharpe | Max DD | Trips |
|---|---|---|---|---|---|---|
| CVX / WFC | 0.0067 | 0.0008 | +3.40% | +0.17 | −15.1% | 14 |
| **MA / V** | 0.0093 | 0.0004 | **+9.97%** | **+1.04** | **−2.2%** | 15 |
| WFC / XOM | 0.0313 | 0.7248 | −2.47% | −0.03 | −12.5% | 13 |
| COP / WFC | 0.0363 | 0.0160 | +0.75% | +0.08 | −16.7% | 10 |
| CVX / XOM | 0.0466 | 0.0123 | −6.03% | −0.45 | −7.5% | 10 |

Two things jump out.

**The p-value ranking did not predict out-of-sample performance.** The best-performing pair by a
wide margin is MA/V — Mastercard and Visa, two duopolists in the same business with the same
customers and the same regulatory exposure. It ranked *second*. The pair that ranked first,
CVX/WFC, is an oil major against a retail bank. There is no economic story that makes those two
revert to each other; the 2018–2021 window just happened to contain a stretch where they did.
Ranking by p-value alone bought the accident and only accidentally also bought the real one.

**WFC/XOM is the clean illustration of a regime break.** It passed in sample at p = 0.031 and
then failed completely out of sample at p = 0.72 — the relationship simply stopped existing.
It lost money, as it should have.

If you traded only the pair with a defensible economic story, you would have gotten Sharpe 1.04
with a 2.2% max drawdown. The statistics were necessary but nowhere near sufficient; the prior
did the real work.

## Multiple comparisons, concretely

12 tickers → 66 tests. At a 5% threshold you expect **3.3 false positives by chance alone**.
The scan found **5 pairs**. So the scan's entire output is roughly consistent with there being
no cointegration anywhere in this universe.

A Bonferroni-corrected threshold is 0.05 / 66 = **0.00076**. **Zero pairs survive it** — not
even MA/V, the one that actually worked. That is the honest state of the evidence: this scan,
at this sample size, cannot distinguish signal from noise on its own.

Scale it up and it gets worse. 50 tickers is 1,225 tests and ~61 expected false positives; the
top of the p-value ranking becomes almost purely a ranking of luck, because you selected on the
noise.

---

## Pitfalls checklist

### Lookahead bias
Any statistic at time t computed with data from after t. Two defenses are built in and both
are verified:

- `rolling_zscore` uses `.rolling(window)`, whose window ends at t. Verified directly: computing
  the z-score on the full series and on the series truncated at bar 400 gives *identical* values
  for the overlapping bars, and identical positions. The full-sample mean and std would have
  failed this.
- `backtest_pair` uses `positions.shift(1)`. You decide at today's close and earn tomorrow's
  return. The test suite pins this: on the bar where the position first goes to +1, the return
  must be exactly 0.

A note on the counterfactual: removing `.shift(1)` on this particular pair produced a *worse*
result (−28% return, Sharpe −1.30), not a better one. That is worth stating plainly, because the
usual claim is "forgetting the shift inflates your backtest." It usually does, but it is not
guaranteed to — what it reliably does is produce a number that has no relationship to what you
could have earned, in either direction. The bug is not "too good"; it is meaningless.

### In-sample selection
The subtler cousin. Pairs are scanned on 2018–2021 and traded on 2022–2024, and beta is
re-estimated on the formation window only — `run_backtest.py` explicitly uses
`hedge_ratio(formation_prices[a], formation_prices[b])`, never the trading window, because
fitting the hedge ratio on data you are about to trade leaks the future into the position size.

What is still contaminated: the *universe* and the *parameters*. I chose 12 tickers, a 60-day
window, and 2.0/0.5 thresholds knowing how markets behaved over this whole period. That is a
soft form of the same bias and no amount of window-splitting fixes it.

### Survivorship bias
The universe is a list of large caps that exist today and that I could name today. Every firm
that was in these sectors in 2018 and subsequently blew up, got acquired, or delisted is absent —
and blow-ups are exactly the regime breaks that kill pairs trades. Yahoo's data cannot fix this;
it has no record of what is no longer listed. The results here are therefore biased upward by an
unknown amount, and any real version of this needs a point-in-time universe (CRSP, Compustat).

### Transaction costs
Costs are charged on `|position change| × 5 bps`, so a 0 → +1 entry costs 5 bps and a +1 → −1
flip costs 10 bps, correctly. On CVX/WFC:

| | Total return | Sharpe |
|---|---|---|
| Gross (0 bps) | +4.90% | 0.230 |
| Net (5 bps) | +3.40% | 0.174 |

Costs ate **31% of the gross return** at 14 round trips over three years — and this is a
low-turnover strategy. 5 bps is also optimistic: it ignores the short-borrow cost on one leg,
which for a genuinely market-neutral book is a real and continuous drag.

### Regime breaks
Cointegration is a property of a sample, not a law of nature. WFC/XOM in the table above is the
worked example: p = 0.031 in sample, p = 0.72 out of sample, money lost. The `stop` threshold in
`generate_positions` exists for exactly this — when |z| keeps growing past 4, the most likely
explanation is not "an even better entry" but "the relationship you were betting on is gone."

---

## Modelling choices worth defending

**Equal dollar weights, not beta weights.** `backtest_pair` uses
`r = pos * (ret_y − ret_x) / 2`, putting half the capital in each leg. beta defines the spread
the *signal* is built on but is not applied to the position. A properly beta-weighted book
needs daily rebalancing, the weights drift with prices, and the rebalancing itself costs money.
The simple version is the standard first pass and is much easier to reason about. Redoing it
properly is a stretch goal.

**ADF critical values are slightly too permissive here.** Because beta is *estimated* rather than
known, the residual has already been optimized to look stationary, so the standard ADF
distribution is the wrong null. `statsmodels.coint()` uses Engle-Granger-specific critical values
and is stricter — verified across five pairs, where it consistently returns a larger p-value
(CVX/WFC: 0.0067 vs 0.0276; MA/V: 0.0093 vs 0.0366). The two agree on every pass/fail call at the
5% threshold, but the direction of the gap is systematic and in the permissive direction.

**Engle-Granger is asymmetric.** Regressing y on x is not the same as x on y, since OLS minimizes
error in the dependent variable only. Where the two orderings disagree materially, that is itself
evidence the relationship is weak.

**Sharpe annualization assumes independent daily returns.** Mean-reversion strategies hold
positions for many bars, so their returns are autocorrelated and the ×√252 scaling is optimistic.
A zero risk-free rate is also assumed, which is standard for quick comparisons but flatters
results in a high-rate environment.

**Hysteresis in the position logic is deliberate.** Entry at |z| = 2.0 and exit at |z| = 0.5 means
the position depends on history, not just the current z, which is why `generate_positions` is a
loop and not a vectorized comparison. A naive `sign(z) * (|z| > entry)` would churn around the
boundary and never hold through the reversion — which is where the entire profit lives.

---

## What I'd do next

1. **Filter the universe by economic linkage first**, then test — MA/V vs CVX/WFC is the whole
   argument in one line.
2. **Half-life of mean reversion** (AR(1) fit on the spread) to set the z-score window from the
   data instead of guessing 60.
3. **Walk-forward**: re-estimate beta each quarter rather than freezing the 2021 value for three
   years. A hedge ratio four years stale is a strong assumption.
4. **Portfolio of pairs** rather than one, so the result does not hinge on a single ranking.
5. **Multiple-comparisons control** (Benjamini-Hochberg over Bonferroni, which is brutal at 66
   tests) applied to the scan itself.

## Reproducing

```bash
pip install -r requirements.txt
pytest -q              # 20 passed
python run_backtest.py # writes backtest.png
```

Note on `src/pairs.ipynb`: the notebook draft defined `hedge_ratio(x, y)` while regressing y on
x, so the parameter names were transposed relative to the call. `src/pairs.py` uses `(y, x)`
throughout, matching the tests and the rest of the pipeline.
