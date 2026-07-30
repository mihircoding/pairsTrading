# Project 1 — Pairs Trading (Statistical Arbitrage)

Build a complete pairs trading research pipeline: find pairs of stocks that move together,
model their spread, trade the spread when it stretches too far, and backtest the whole thing
honestly.

This is the classic first stat-arb project because it touches everything: data handling,
statistics (cointegration and stationarity), signal generation, backtesting, and performance
evaluation. If you can explain every step of this pipeline in an interview, you're in good
shape.

## The idea

Some pairs of assets are tied together economically — two oil majors, two exchange operators,
an ETF and its largest holding. Their individual prices wander (they're non-stationary), but
some *combination* of them tends to snap back to an equilibrium.

Pairs trading bets on that snap-back:

1. Find two assets whose price relationship is stable (they are **cointegrated**).
2. Compute the **spread**: `spread = price_A - beta * price_B`, where `beta` is the hedge ratio.
3. When the spread is unusually wide, short the expensive leg and buy the cheap one.
4. Close the position when the spread reverts to its mean.

Because you're long one asset and short the other, you're roughly market-neutral: you don't
care whether the market goes up or down, only whether the *relationship* reverts.

## Correlation is not cointegration

This is the single most important concept in the project, and a common interview question.

- **Correlation** measures whether daily *returns* move together. Two stocks can be highly
  correlated while drifting arbitrarily far apart in *price* (one just grows faster).
- **Cointegration** means a linear combination of the *prices* is stationary — it has a
  stable mean it keeps coming back to. That mean-reverting combination is what you can trade.

You test for cointegration with the **Engle-Granger two-step method**:

1. Regress `price_A` on `price_B` (ordinary least squares). The slope is the hedge ratio `beta`.
2. Take the residuals of that regression (the spread) and run an **Augmented Dickey-Fuller
   (ADF) test** on them. The ADF null hypothesis is "this series has a unit root" (i.e., it's
   a random walk). A low p-value (< 0.05) means you can reject that — the spread is
   stationary, and the pair is cointegrated.

`statsmodels` provides both pieces (`OLS` and `adfuller`), plus a combined `coint()` function
you can use to sanity-check your own implementation.

## The signal: rolling z-score

Once you have a spread, standardize it so "unusually wide" means the same thing at any point
in time:

```
z = (spread - rolling_mean(spread, window)) / rolling_std(spread, window)
```

The trading rules are threshold-based:

- `z > +entry` (e.g., +2.0): spread too wide → **short the spread** (short A, long beta*B)
- `z < -entry`: spread too narrow → **long the spread**
- `|z| < exit` (e.g., 0.5): spread has reverted → **flatten**
- Optional stop: `|z| > stop` (e.g., 4.0): the relationship may have broken → get out

Why a *rolling* window instead of the full-sample mean and std? Because using the full sample
means your signal at time t knows about data from the future. That's **lookahead bias**, and
it's the most common way beginners accidentally build a money printer that only works on
paper.

## Repo layout

```
01-pairs-trading/
├── README.md
├── requirements.txt
├── run_backtest.py        # example driver script showing the intended API
├── src/
│   ├── data.py            # data download + caching (complete — read it, don't rewrite it)
│   ├── pairs.py           # TODO: hedge ratio, Engle-Granger test, pair scanning
│   ├── signals.py         # TODO: spread, rolling z-score, position logic
│   └── backtest.py        # TODO: vectorized backtest + performance metrics
└── tests/
    ├── test_pairs.py
    ├── test_signals.py
    └── test_backtest.py
```

## Build it: milestones

Work in this order. Each milestone has matching tests.

**Milestone 1 — Hedge ratio** (`src/pairs.py :: hedge_ratio`)
OLS regression of y on x with an intercept. Return the slope. The test generates
`y = 2.5 * x + noise` and checks you recover ~2.5.
Run: `pytest tests/test_pairs.py -k hedge`

**Milestone 2 — Cointegration test** (`src/pairs.py :: engle_granger_pvalue`)
Regress, take residuals, ADF-test the residuals, return the p-value. The tests feed you one
truly cointegrated synthetic pair and one pair of independent random walks — your function
must tell them apart.
Run: `pytest tests/test_pairs.py -k engle`

**Milestone 3 — Pair scanning** (`src/pairs.py :: find_cointegrated_pairs`)
Loop over all ticker combinations, test each, return pairs sorted by p-value. Think about
the multiple-comparisons problem: test 50 tickers and you have 1,225 pairs — at a 5%
threshold you expect ~60 false positives *by chance alone*. This is why pairs found by
pure statistical scanning often fall apart out of sample.

**Milestone 4 — Signals** (`src/signals.py`)
Compute the spread, the rolling z-score, and the position series (+1 long spread, -1 short,
0 flat) using the entry/exit thresholds. Two things the tests check hard:

- No lookahead: the z-score at time t uses only data up to t.
- Positions must be **shifted by one bar** before being applied to returns — you decide at
  today's close, you trade at tomorrow's. Forgetting `.shift(1)` inflates every backtest.

**Milestone 5 — Backtest and metrics** (`src/backtest.py`)
Compute daily strategy returns from positions and spread changes, subtract transaction
costs on position *changes*, and produce an equity curve. Then implement the metrics
every quant conversation assumes you know cold:

- **Sharpe ratio** (annualized: mean/std of daily returns × √252)
- **Max drawdown** (worst peak-to-trough drop of the equity curve)
- **Total return** and **number of round trips**

**Milestone 6 — Run it on real data**
`run_backtest.py` downloads a small universe of related tickers, scans for pairs on a
*formation window* (e.g., 2018–2021), then trades the best pair on a *later* window
(2022–2024). Never scan and trade on the same data — that's in-sample selection, the
subtler cousin of lookahead bias.

## Pitfalls checklist (put this in your write-up)

- **Lookahead bias** — any statistic at time t computed with data after t. Rolling windows
  and `.shift(1)` are the defenses.
- **In-sample selection** — picking pairs on the same period you backtest. Use separate
  formation and trading windows.
- **Survivorship bias** — Yahoo's current ticker list omits delisted companies. Your
  universe is already biased toward survivors. Know this and say it.
- **Transaction costs** — a strategy trading daily at 10 bps per trade loses ~25% a year
  to costs before it earns anything. Always report results net of costs.
- **Regime breaks** — cointegration is a statistical property, not a law. Pairs break
  (see: every pairs trader in 2008). The stop-loss threshold exists for this reason.

## Stretch goals

- Replace the fixed OLS hedge ratio with a **rolling** or **Kalman-filter** hedge ratio
  (the `pykalman` route is a classic; implementing the filter yourself from the update
  equations is better).
- Compute the spread's **half-life of mean reversion** (fit an Ornstein-Uhlenbeck /
  AR(1) model to the spread) and use it to set the z-score window instead of guessing.
- Walk-forward analysis: re-estimate the hedge ratio and thresholds each quarter.
- Portfolio of pairs: trade the top 5 pairs simultaneously and look at how the combined
  Sharpe compares to the individual ones.

## Resources

- Ernest Chan, *Algorithmic Trading: Winning Strategies and Their Rationale* — chapters 2–3
  are the standard practitioner treatment of mean reversion and cointegration.
- Gatev, Goetzmann & Rouwenhorst (2006), "Pairs Trading: Performance of a Relative-Value
  Arbitrage Rule" — the academic paper that started it; free on SSRN.
- statsmodels docs on `adfuller` and `coint`: https://www.statsmodels.org/stable/tsa.html
- Hudson & Thames' open articles on pairs selection: https://hudsonthames.org/research/
- QuantStart's pairs trading and cointegration articles: https://www.quantstart.com/articles/
- For the Kalman stretch goal: Chan's book ch. 3, and the `pykalman` documentation.
