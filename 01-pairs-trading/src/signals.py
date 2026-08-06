"""Signal generation: spread, rolling z-score, and positions.

Milestone 4. Verify with:  pytest tests/test_signals.py
"""

import numpy as np
import pandas as pd


def compute_spread(y: pd.Series, x: pd.Series, beta: float) -> pd.Series:
    """spread = y - beta * x.

    This is the tradeable object. Neither y nor x is stationary on its own —
    each wanders like a random walk — but if the pair is cointegrated this
    particular combination of them has a mean it keeps returning to.

    beta is deliberately a scalar fixed outside this function, estimated on the
    formation window. Re-estimating it on the data you are about to trade would
    leak the future into the hedge ratio.
    """
    return y - beta * x


def rolling_zscore(spread: pd.Series, window: int = 60) -> pd.Series:
    """Standardize the spread against its own trailing history.

        z_t = (spread_t - mean(spread_{t-window+1..t})) / std(same window)

    Why rolling rather than full-sample: the full-sample mean and standard
    deviation are computed from the entire series, including bars after t. Using
    them would mean the signal at time t knows where the spread eventually
    settles — lookahead bias, and the single most common way a backtest turns
    into a money printer that only works on paper.

    pandas' .rolling(window) window ENDS at t, so it is already causal. The
    first window-1 values are NaN by construction; that warm-up period is real
    and is left in place rather than back-filled.

    std uses ddof=1 (pandas' default), the sample standard deviation.
    """
    rolling = spread.rolling(window)
    return (spread - rolling.mean()) / rolling.std()


def generate_positions(
    zscore: pd.Series,
    entry: float = 2.0,
    exit: float = 0.5,
) -> pd.Series:
    """Turn the z-score into a position in the SPREAD: +1, -1, or 0.

    Rules, evaluated bar by bar:
      - flat  and z < -entry  -> long the spread  (+1): spread unusually narrow,
                                 so buy y and short beta * x, betting it widens
      - flat  and z > +entry  -> short the spread (-1): spread unusually wide
      - long  and z >= -exit  -> flatten; otherwise hold
      - short and z <= +exit  -> flatten; otherwise hold
      - NaN z (the warm-up window, or a zero-variance stretch) -> flat

    This is a state machine, not a vectorizable comparison, and the reason is
    HYSTERESIS: the entry threshold (2.0) and the exit threshold (0.5) differ,
    so what you do at z = 1.2 depends on whether you are already in a trade.
    A naive `np.sign(z) * (abs(z) > entry)` would churn in and out around the
    boundary and would never hold a position through the reversion, which is
    where the entire profit lives.

    The band between exit and entry is intentionally a no-trade zone when flat:
    it stops the strategy from re-entering on noise right after taking profit.

    A plain loop is the honest first implementation. It is O(n) and n is a few
    thousand bars, so the vectorized ffill trick is not worth the bugs.
    """
    positions = np.zeros(len(zscore), dtype=int)
    state = 0

    for i, z in enumerate(zscore.to_numpy(dtype=float)):
        if np.isnan(z):
            state = 0
        elif state == 0:
            if z > entry:
                state = -1
            elif z < -entry:
                state = 1
        elif state == 1:  # long the spread, waiting for it to widen back to 0
            if z >= -exit:
                state = 0
        else:  # state == -1, short the spread
            if z <= exit:
                state = 0
        positions[i] = state

    return pd.Series(positions, index=zscore.index, dtype=int)
