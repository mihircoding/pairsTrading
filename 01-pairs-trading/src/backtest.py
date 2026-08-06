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

    Return model (deliberately the simple one):

        r_t = pos_{t-1} * (ret_y_t - ret_x_t) / 2

    i.e. equal DOLLAR weights on the two legs, half the capital in each, so
    r_t is the return on the whole book rather than on one leg. beta is not
    applied here — it defines the spread the *signal* is built on, but a
    beta-weighted, daily-rebalanced book is a different and messier object
    (weights drift with prices, and rebalancing them costs money). Equal
    dollar legs is the standard first-pass approximation; the stretch goal is
    to redo this properly and compare.

    THE SHIFT is the load-bearing line. positions.shift(1) encodes "I saw
    today's close, formed a signal, and traded at the next bar." Without it,
    bar t's return is earned by a position chosen using bar t's own prices —
    you would be buying the spread on the day it moves, every time. Skipping
    .shift(1) is the single most effective way to fake a great Sharpe.

    Costs are charged on |change in position|, because that is when shares
    actually move. Going 0 -> +1 trades one unit; flipping +1 -> -1 trades two,
    and is charged double, correctly. The first bar is compared against an
    implicit flat book.

    Returns a DataFrame with ['ret', 'ret_net', 'equity'] indexed like y.
    """
    # Align everything to y's index so a mismatched signal can't silently
    # shift returns by a day.
    x = x.reindex(y.index)
    positions = positions.reindex(y.index).fillna(0)

    ret_y = y.pct_change()
    ret_x = x.pct_change()

    lagged = positions.shift(1)
    ret = (lagged * (ret_y - ret_x) / 2.0).fillna(0.0)

    # Prior to the first bar the book is flat, so the opening trade is charged.
    turnover = positions.diff()
    turnover.iloc[0] = positions.iloc[0]
    cost = turnover.abs() * (cost_bps / 10_000.0)

    ret_net = ret - cost
    equity = (1.0 + ret_net).cumprod()

    return pd.DataFrame({"ret": ret, "ret_net": ret_net, "equity": equity}, index=y.index)


def sharpe_ratio(daily_returns: pd.Series) -> float:
    """Annualized Sharpe: mean(r) / std(r) * sqrt(252), risk-free rate = 0.

    Sample std (ddof=1). Assuming a zero risk-free rate is standard for quick
    strategy comparisons but is not free: in a 5% rate environment it flatters
    every strategy, and it flatters a market-neutral book like this one less
    than a long-only one, since the short leg earns a rebate. Say so in a
    write-up rather than pretending the choice doesn't exist.

    The sqrt(252) scaling assumes returns are independent across days. Mean
    reversion strategies hold positions for many bars, so their returns are
    autocorrelated and this annualization is optimistic.
    """
    r = daily_returns.dropna()
    if len(r) < 2:
        return 0.0
    sd = r.std(ddof=1)
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float(r.mean() / sd * np.sqrt(TRADING_DAYS))


def max_drawdown(equity: pd.Series) -> float:
    """Worst peak-to-trough decline of the equity curve, as a NEGATIVE number.

    drawdown_t = equity_t / running_max(equity)_t - 1

    Sharpe treats an up-move and a down-move as equally informative; drawdown
    asks the question a person with money in the fund actually asks, which is
    how bad it got and for how long. A strategy can have a respectable Sharpe
    and still be untradeable because nobody could sit through the drawdown.
    """
    eq = equity.dropna()
    if eq.empty:
        return 0.0
    drawdown = eq / eq.cummax() - 1.0
    return float(drawdown.min())


def summarize(result: pd.DataFrame, positions: pd.Series) -> dict:
    """The numbers you'd put in a README table.

    A round trip is one entry into a nonzero position that later returns to
    flat, counted as nonzero -> zero transitions. A position still open on the
    last bar is not counted: it has not paid out yet.

    n_round_trips is the sanity check on everything else. Two trades over three
    years means the metrics rest on two observations and mean nothing. Several
    hundred means costs, not signal, will dominate the result.
    """
    equity = result["equity"].dropna()
    total_return = float(equity.iloc[-1] - 1.0) if not equity.empty else 0.0

    pos = positions.reindex(result.index).fillna(0)
    prev = pos.shift(1).fillna(0)
    n_round_trips = int(((prev != 0) & (pos == 0)).sum())

    return {
        "total_return": total_return,
        "sharpe": sharpe_ratio(result["ret_net"]),
        "max_drawdown": max_drawdown(result["equity"]),
        "n_round_trips": n_round_trips,
    }
