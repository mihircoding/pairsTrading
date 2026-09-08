# Results

## The scan

4,950 pairs tested across the S&P 100 (`scan.py`, formation window
2013-01-01 - 2020-12-31, Engle-Granger p-value on each pair's OLS residuals).

| | |
|---|---|
| Pairs tested | 4,950 |
| Passed at 5% | 930 (18.8%) |
| Expected false positives at 5%, by chance alone | ~247.5 |
| Bonferroni threshold (0.05 / 4,950) | 1.01e-05 |
| Pairs surviving Bonferroni | **1** (ACN / LIN) |

930 pairs "pass" a 5% threshold when random chance alone predicts ~248 false
positives out of 4,950 tests - the multiple-comparisons problem the
project's own pitfalls checklist warns about, made concrete. Almost all of
those 930 are noise. Only one pair, ACN/LIN, survives correcting for testing
4,950 hypotheses at once.

## Trading the one pair that's statistically real

Formation-window OLS gives ACN/LIN a hedge ratio of 0.9317. Trading that
fixed beta out of sample (2021-01-04 - 2025-12-30, same z-score rule as
every other pair in the scan: 60-bar window, entry 2.0, exit 0.5, 5bps cost):

| | |
|---|---|
| Total return | **-6.06%** |
| Sharpe | **-0.11** |
| Max drawdown | -23.54% |
| Round trips | 23 |
| Out-of-sample ADF p-value | 0.179 |

The pair that passed the hardest statistical bar available didn't just lose
money out of sample - it doesn't even test as cointegrated anymore in the
trading window (p=0.18, nowhere near 0.05). Whatever tied ACN and LIN
together in 2013-2020 either weakened or the fixed beta stopped describing
it. Either way, this is the project's honest headline: passing a
Bonferroni-corrected test on formation data is necessary for "this pair
isn't noise," but it is nowhere near sufficient for "this pair is
tradeable."

## Is that the fixed hedge ratio's fault?

`kalman_vs_static.py` asks that directly instead of assuming an answer.
Same pair, same trading-window prices, same z-score rule, same costs - the
only change is a from-scratch Kalman filter (`src/pairs.ipynb ::
kalman_hedge_ratio`, the stretch goal below) tracking beta continuously
through formation *and* trading, instead of freezing it at the end of
formation.

| | total return | Sharpe | max dd | round trips |
|---|---|---|---|---|
| Static beta (0.9317, frozen) | -6.06% | -0.11 | -23.54% | 23 |
| Kalman beta (continuously updated) | **+3.79%** | **+0.16** | **-10.97%** | 37 |

The Kalman beta starts trading at 0.976 - close to the static value, as it
should be, since it's seen the same formation data - and drifts to 0.632 by
the end of 2025. That's a real, substantial move in the actual relationship
between these two stocks, not filter noise: a hedge ratio frozen in 2020
was pricing the spread against a relationship that had already changed by
2023-2025. Letting beta track that drift turns a losing strategy into a
small winner with roughly half the drawdown - at the cost of 14 extra round
trips (37 vs 23), which is exactly what you'd expect from a beta that's
allowed to keep moving.

**What this does and doesn't show.** One pair, one delta setting, no
transaction-cost sensitivity on the extra turnover, no walk-forward
validation of the Kalman parameters themselves. It does not rescue the
project's headline finding - a single pair flipping from a small loss to a
small gain under a smarter estimator is not evidence that stat-arb "works,"
and 4,949 other pairs still failed the Bonferroni bar entirely regardless
of what hedge ratio they'd have used. What it does show: for the one pair
that cleared the statistical bar, the specific way it lost money out of
sample (a stale hedge ratio, not a broken relationship) was diagnosable and
partially fixable. That distinction - "this pair is real but was traded
wrong" vs. "this pair was never real" - is exactly the kind of honest
follow-up question a scan like this one should raise.

## Stretch goals

- **Kalman-filter hedge ratio** - done, see above and
  `src/pairs.ipynb :: kalman_hedge_ratio`. Implemented from the update
  equations (not `pykalman`): a single-state filter tracking `beta_t`
  through-origin, matching this project's own `compute_spread = y - beta *
  x` convention (no separately-floating intercept - see the function's
  docstring for why that would actually be a worse model here, not just a
  simpler one). 6 new tests in `tests/test_kalman.py`.
- **Use `half_life()` to set the z-score window per pair** instead of the
  fixed 60-bar default used everywhere above - still open.
- **Walk-forward analysis**: re-estimate hedge ratios and thresholds each
  quarter rather than once per multi-year window.
- **Portfolio of pairs**: trade the top 930 (or top N) simultaneously and
  look at the combined Sharpe against the individual ones - probably the
  most direct way to find out whether *any* aggregate edge survives once
  you stop cherry-picking one pair to look at.

## Caveats (unchanged by any of the above)

- **Survivorship bias**: the universe is the S&P 100 as it stands today, so
  the scan asks how today's winners behaved on their way to winning.
- Prices are Yahoo Finance `Close` (auto-adjusted) - fine for research,
  not for anything live.
- Transaction costs are modeled as a flat 5bps per side; nothing here is
  investment advice.
