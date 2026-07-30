"""Mean-variance optimization with real-world constraints.

Milestones 2-3. Verify with:  pytest tests/test_optimizer.py

The scipy pattern you'll reuse for both problems (and for the frontier):

    from scipy.optimize import minimize

    n = len(mu)
    result = minimize(
        objective,                       # function of w to MINIMIZE
        x0=np.full(n, 1 / n),            # start at equal weight
        method="SLSQP",
        bounds=[(0.0, 1.0)] * n,         # long-only; None-bounds = shorting allowed
        constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}],
    )
    weights = result.x

Always check result.success — a silently failed optimize returning x0 is a
classic source of "why are all my portfolios equal weight?".
"""

import numpy as np


def portfolio_performance(w: np.ndarray, mu: np.ndarray, cov: np.ndarray,
                          rf: float = 0.0) -> tuple[float, float, float]:
    """Milestone 2a: return (expected_return, volatility, sharpe).

    ret = w @ mu
    vol = sqrt(w @ cov @ w)
    sharpe = (ret - rf) / vol     (0.0 if vol is 0)
    """
    raise NotImplementedError("Milestone 2")


def min_variance_weights(cov: np.ndarray, long_only: bool = True) -> np.ndarray:
    """Milestone 2b: the global minimum-variance portfolio.

    Minimize w @ cov @ w subject to sum(w) = 1 (and 0 <= w <= 1 if long_only).
    Note mu is not an argument — this portfolio needs no return forecasts,
    which is exactly why practitioners trust it more than max-Sharpe.
    """
    raise NotImplementedError("Milestone 2")


def max_sharpe_weights(mu: np.ndarray, cov: np.ndarray, rf: float = 0.0,
                       long_only: bool = True) -> np.ndarray:
    """Milestone 3: the tangency portfolio.

    Minimize the NEGATIVE Sharpe ratio (scipy only minimizes). Reuse
    portfolio_performance inside the objective.
    """
    raise NotImplementedError("Milestone 3")
