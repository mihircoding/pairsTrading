"""Trace the efficient frontier.

Milestone 4. Verify with:  pytest tests/test_frontier.py
"""

import numpy as np
import pandas as pd


def efficient_frontier(mu: np.ndarray, cov: np.ndarray, n_points: int = 30,
                       long_only: bool = True) -> pd.DataFrame:
    """For each target return, find the minimum-variance portfolio achieving it.

    Sweep targets: np.linspace(mu.min(), mu.max(), n_points) — with long-only
    weights you cannot achieve returns outside the assets' own range, so this
    is exactly the feasible span.

    For each target, solve min-variance with ONE EXTRA constraint on top of the
    Milestone 2 setup:
        {"type": "eq", "fun": lambda w: w @ mu - target}
    (Watch the closure-over-loop-variable trap: bind target as a default arg,
    `lambda w, t=target: w @ mu - t`.)

    Return a DataFrame with columns ['target_return', 'volatility', 'weights']
    (weights as np.ndarray per row), skipping any target where the optimizer
    fails to converge.
    """
    raise NotImplementedError("Milestone 4")
