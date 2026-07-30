# Quant Development Project Templates

Five hands-on Python projects covering the core skills quantitative developers use day to day:
statistical arbitrage, backtesting infrastructure, derivatives pricing, market microstructure,
and portfolio construction.

These are **learning templates, not finished libraries**. Each project ships with:

- a README that explains the theory and walks through the build step by step
- skeleton source files where the important functions are left for you to implement
  (each one has a docstring spelling out inputs, outputs, and hints)
- a test suite that verifies your implementation, so you know when you got it right

The idea is simple: read the README, implement the TODOs one milestone at a time, and run
the tests until they pass. By the end of each project you will have written every line of
the interesting code yourself.

## The projects

| # | Project | What you learn |
|---|---------|----------------|
| 1 | [Pairs Trading](01-pairs-trading/) | Cointegration, mean reversion, z-score signals, vectorized backtesting, performance metrics |
| 2 | [Event-Driven Backtester](02-backtesting-engine/) | Software architecture for trading systems, event queues, portfolio accounting, execution simulation |
| 3 | [Options Pricing Lab](03-options-pricing/) | Black-Scholes, binomial trees, Monte Carlo methods, Greeks, implied volatility |
| 4 | [Limit Order Book](04-limit-order-book/) | Market microstructure, price-time priority, matching engines, order flow simulation |
| 5 | [Portfolio Optimization](05-portfolio-optimization/) | Mean-variance optimization, the efficient frontier, covariance estimation, risk parity |

## Suggested order

Work through them in numbered order. Pairs trading (1) introduces the pandas/numpy workflow
everything else builds on. The backtester (2) is the biggest software engineering exercise.
Options (3) and the order book (4) are self-contained and can be swapped. Portfolio
optimization (5) ties the statistics back together.

Each project is independent — you can clone the repo and start anywhere.

## Setup

Python 3.10+ recommended. Each project has its own `requirements.txt`:

```
cd 01-pairs-trading
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pytest                        # run the tests (they fail until you implement the TODOs)
```

## How to work through a project

1. Read the project README top to bottom before writing any code.
2. Implement one milestone at a time. Run only that milestone's tests
   (`pytest tests/test_pairs.py -k hedge_ratio`) until they pass.
3. When all tests pass, do the stretch goals — that is where the real learning is.
4. Write up what you found. A short RESULTS.md with plots and honest numbers
   (including the strategies that *didn't* work) is worth more to a recruiter
   than green checkmarks.

## A note on honesty

Backtests lie easily. Every README here has a "pitfalls" section covering lookahead bias,
survivorship bias, transaction costs, and overfitting. Understanding *why* a strategy's
Sharpe ratio collapses out of sample is the actual skill being tested in quant interviews.

None of this is investment advice. The data pipelines here use free data sources
(Yahoo Finance) which are fine for learning and completely inadequate for live trading.
