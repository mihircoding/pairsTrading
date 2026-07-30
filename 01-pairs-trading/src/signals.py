"""Signal generation: spread, rolling z-score, and positions.

Milestone 4. Verify with:  pytest tests/test_signals.py
"""

import pandas as pd


def compute_spread(y: pd.Series, x: pd.Series, beta: float) -> pd.Series:
    """spread = y - beta * x. One line — the point is naming the concept."""
    raise NotImplementedError("Milestone 4")


def rolling_zscore(spread: pd.Series, window: int = 60) -> pd.Series:
    """Standardize the spread against its own rolling history.

    z_t = (spread_t - mean(spread over last `window` bars))
          / std(spread over last `window` bars)

    Requirements:
      - Use ONLY past data at each point: pandas .rolling(window) already does
        this (the window at time t ends AT t). Do not use the full-series mean
        or std — that is lookahead bias.
      - The first `window - 1` values will be NaN. That is correct; leave them.
    """
    raise NotImplementedError("Milestone 4")


def generate_positions(
    zscore: pd.Series,
    entry: float = 2.0,
    exit: float = 0.5,
) -> pd.Series:
    """Turn the z-score into a position in the SPREAD: +1, -1, or 0.

    Rules (state machine, evaluated bar by bar):
      - flat  and z < -entry  -> go long the spread  (+1)
      - flat  and z > +entry  -> go short the spread (-1)
      - long  and z >= -exit  -> flatten (0); otherwise stay long
      - short and z <= +exit  -> flatten (0); otherwise stay short
      - NaN z-score -> stay flat

    Note this is NOT vectorizable with a couple of comparisons, because whether
    you're in a position depends on history (hysteresis: you enter at 2.0 but
    exit at 0.5). A plain Python loop over the series is fine and is the honest
    way to write it first. If you later want speed, look up how to vectorize
    state machines with ffill tricks — but get the loop right first.

    Return an integer-valued Series aligned to `zscore`.
    """
    raise NotImplementedError("Milestone 4")
