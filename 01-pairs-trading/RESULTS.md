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

## Trading all of them at once

Everything above rests on one pair. That is a fair headline and a fragile
one - ACN/LIN is a single draw, and a single draw can say anything. The
README has listed the fix as a stretch goal from the start: trade the
survivors as a portfolio and ask whether *any* aggregate edge is there once
you stop picking one pair to look at. `portfolio.py` does that.

Every one of the 930 survivors, re-run through the same backtest (same
formation beta, same 60-bar z-score, same entry 2.0 / exit 0.5, same 5bps),
then equal-weighted. Taking the top N by formation p-value:

| N pairs | total return | Sharpe | max dd | ann vol |
|---|---|---|---|---|
| 1 | −6.06% | −0.11 | −23.54% | 8.30% |
| 5 | +4.46% | 0.17 | −9.68% | 6.59% |
| 10 | +6.44% | 0.32 | −6.35% | 4.19% |
| 25 | +5.45% | **0.34** | −5.21% | 3.29% |
| 50 | +1.74% | 0.12 | −6.02% | 3.20% |
| 100 | +0.97% | 0.08 | −4.42% | 2.75% |
| 250 | −1.06% | −0.07 | −4.26% | 2.49% |
| 500 | −1.25% | −0.10 | −2.78% | 2.18% |
| 930 | −2.14% | −0.19 | −4.04% | 2.13% |

The top-25 book at 0.34 is the most flattering number this project has
produced, and it is the one to be most careful with: N was chosen after
seeing the column. The honest reading of that table is the whole shape, and
the whole shape says the peak is where a peak has to be when you sweep a
parameter over noise.

### Does the screen rank anything?

If the formation p-value carries information, the strongest survivors should
out-trade the weakest. Split the 930 into five equal buckets by p-value and
trade each as its own book:

| Bucket | p-value range | total return | Sharpe |
|---|---|---|---|
| 1 (strongest) | 6.8e-08 – 3.8e-03 | −2.50% | −0.17 |
| 2 | 3.9e-03 – 1.1e-02 | +0.41% | 0.05 |
| 3 | 1.1e-02 – 2.3e-02 | −1.90% | −0.15 |
| 4 | 2.3e-02 – 3.5e-02 | −3.32% | −0.28 |
| 5 (weakest) | 3.5e-02 – 5.0e-02 | −3.51% | −0.28 |

There is a hint of a gradient in the bottom half and none at the top: the
strongest bucket does worse than the second. Across all 930 pairs the rank
correlation between formation p-value and out-of-sample Sharpe is **−0.053**
(z = −1.6 against the null of no association) - the direction you would want,
and nowhere near large enough to act on.

That −0.05 has been quoted in this repo's README since the first scan.
What's new is that it is now reproducible from `portfolio.py` rather than an
unsourced number, and that it comes with the thing it implies: a book built
from the strongest fifth of the survivors does not beat a book built from
the weakest fifth. **The screen does not rank.** Eight years of formation
data, a test with a Nobel in its ancestry, 4,950 hypotheses - and the
resulting ordering carries about as much information as a coin.

That is a stronger statement than the ACN/LIN result, because it is made
across 930 pairs instead of one.

### Where the book's Sharpe comes from

| | |
|---|---|
| Mean single-pair Sharpe | −0.009 |
| Median single-pair Sharpe | −0.008 |
| Share of pairs with positive Sharpe | 48.8% |
| Share of pairs that actually made money | 41.8% |
| Average pairwise correlation of pair returns | 0.033 |
| Book Sharpe, predicted by the arithmetic | −0.05 |
| Book Sharpe, realized equal-risk | −0.05 |
| Book Sharpe, realized equal-weight | −0.19 |

Just under half the pairs have a positive Sharpe. That is a coin, and it is
the finding: the survivors' returns are centered on zero, so averaging them
gives zero however many you average.

The two "share" rows are worth separating, because they are not the same
test and the repo has quoted both. 48.8% have a positive mean daily return;
only 41.8% finish the trading window above where they started. The seven
points in between are volatility drag - a spread strategy that averages zero
compounds to slightly less than zero, and the wider the swings the more it
loses to that. Nothing is wrong with either number; they answer different
questions, and the second is the one an investor would ask.

The arithmetic is worth spelling out because it is the reason a portfolio
cannot rescue this. Averaging N equally-risked series with mean pairwise
correlation ρ multiplies Sharpe by `sqrt(N) / sqrt(1 + (N-1)ρ)`. At ρ = 0.033
and N = 930 that factor is about 5.4, and it is applied to a mean pair
Sharpe of −0.009. Diversification works exactly as advertised here - it
faithfully magnifies a number that is zero.

The gap between the two realized rows is its own small lesson. The prediction
is about equally-*risked* series, and these pairs' volatilities span 6.8x. The
correlation between a pair's volatility and its out-of-sample Sharpe is −0.27:
the noisier pairs did worse. Equal *dollar* weighting therefore hands the most
risk to the pairs that deserve the least, which is where −0.05 becomes −0.19.
Equal-risk weighting uses trading-window volatility and so isn't a strategy
anyone could have run - it is a diagnostic, and what it diagnoses is that
even the sizing question was working against the book.

### And it isn't 930 independent bets anyway

930 pairs drawn from 100 tickers is 1,860 legs over 100 names. The most
frequent leg is GILD at 65 pairs - 3.5% of the book's gross exposure in one
stock, before counting the 64 different things it is paired against. A book
like this is a handful of concentrated single-name positions wearing 930
labels, and the ρ = 0.033 above is small largely because the legs point in
different directions, not because the bets are unrelated.

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
- ~~**Portfolio of pairs**~~ - done, see "Trading all of them at once"
  above and `portfolio.py`. The equal-weight book of all 930 returns
  -2.14% at a Sharpe of -0.19, 48.8% of pairs make money, and the
  formation p-value's rank correlation with out-of-sample Sharpe is
  -0.05. 17 tests in `tests/test_portfolio.py`.

## Caveats (unchanged by any of the above)

- **Survivorship bias**: the universe is the S&P 100 as it stands today, so
  the scan asks how today's winners behaved on their way to winning.
- Prices are Yahoo Finance `Close` (auto-adjusted) - fine for research,
  not for anything live.
- Transaction costs are modeled as a flat 5bps per side; nothing here is
  investment advice.
