"""Vectorized backtest and performance metrics.

Milestone 5. Verify with:  pytest tests/test_backtest.py

Conventions used throughout:
  - "position" is the position in the spread at each bar: +1, -1, or 0
  - returns are simple daily returns, equity curve starts at 1.0
  - costs are charged when the position CHANGES (that's when you trade)
"""

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def backtest_pair(
    y: pd.Series,
    x: pd.Series,
    beta: float,
    positions: pd.Series,
    cost_bps: float = 5.0,
) -> pd.DataFrame:
    """Compute daily strategy returns for a pairs trade.

    Steps:
      1. Dollar-neutral leg returns: the strategy return of the spread position is
             r_t = pos_{t-1} * (ret_y_t - beta_adj * ret_x_t) / 2
         where ret_y, ret_x are simple daily returns of each leg and
         beta_adj = beta * (x / y) rebalanced...

         KEEP IT SIMPLE for the first pass: use
             r_t = pos_{t-1} * (ret_y_t - ret_x_t) / 2
         i.e., equal dollar weights on each leg. It is a fine approximation for
         a first backtest and much easier to reason about. (Stretch goal:
         do proper beta-weighted, daily-rebalanced legs and compare.)

      2. THE SHIFT: use pos.shift(1), not pos. You decide at today's close and
         earn tomorrow's return. The tests will fail if you skip this.

      3. Costs: each unit of position change trades both legs. Charge
             cost_t = |pos_t - pos_{t-1}| * cost_bps / 10000
         and subtract it from that day's return.

      4. Equity curve: (1 + r_net).cumprod()

    Return a DataFrame with columns ['ret', 'ret_net', 'equity'] indexed like y.
    """
    raise NotImplementedError("Milestone 5")


def sharpe_ratio(daily_returns: pd.Series) -> float:
    """Annualized Sharpe: mean(r) / std(r) * sqrt(252).

    Use sample std (ddof=1). If std is 0 or the series is empty, return 0.0
    rather than dividing by zero. (Assumes 0 risk-free rate, which is standard
    for quick strategy comparisons — say so in your write-up.)
    """
    raise NotImplementedError("Milestone 5")


def max_drawdown(equity: pd.Series) -> float:
    """Worst peak-to-trough decline of the equity curve, as a NEGATIVE number.

    drawdown_t = equity_t / running_max(equity)_t - 1
    return drawdown.min()

    Hint: .cummax()
    """
    raise NotImplementedError("Milestone 5")


def summarize(result: pd.DataFrame, positions: pd.Series) -> dict:
    """Small convenience: the numbers you'd put in a README table.

    Return {'total_return', 'sharpe', 'max_drawdown', 'n_round_trips'}.
    A round trip = an entry into a nonzero position that later returns to flat.
    """
    raise NotImplementedError("Milestone 5")
