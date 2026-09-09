# Pairs Trading

**[Live site &rarr;](https://mihircoding.github.io/pairsTrading/)** — the full scan, every surviving pair, and a browser-side backtest you can re-run with your own parameters.

A statistical arbitrage study on the S&P 100: screen every pair for cointegration on a
formation window, then trade the survivors out of sample and see whether the screen actually
predicted anything.

Short version — it didn't. 4,950 pairs tested, 930 passed at 5%, one survived Bonferroni,
and the mean out-of-sample Sharpe across the survivors was indistinguishable from zero.
The write-up leads with that rather than the top of the leaderboard.

## Layout

| Path | What it is |
|---|---|
| [`01-pairs-trading/src/pairs.ipynb`](01-pairs-trading/src/pairs.ipynb) | The pipeline, built up step by step on a 12-ticker universe |
| [`01-pairs-trading/scan.py`](01-pairs-trading/scan.py) | The full S&P 100 scan — writes everything to `results/` |
| [`01-pairs-trading/app.py`](01-pairs-trading/app.py) | Streamlit explorer over those results |
| [`01-pairs-trading/README.md`](01-pairs-trading/README.md) | The theory: cointegration vs correlation, Engle-Granger, the pitfalls |
| [`docs/`](docs/) | Static version of the explorer for GitHub Pages |

## Running it

```
cd 01-pairs-trading
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
python scan.py          # ~65s, builds results/
streamlit run app.py
```

## Caveats

Survivorship bias: the universe is the S&P 100 as it stands today, so the backtest asks how
today's winners behaved on their way to winning. Fixing it needs point-in-time constituents
(CRSP, Compustat), which free data doesn't provide.

Prices come from Yahoo Finance — fine for this, useless for anything live. None of this is
investment advice.
