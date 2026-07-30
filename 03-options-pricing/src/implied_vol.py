"""Implied volatility: invert Black-Scholes for sigma.

Milestone 5. Verify with:  pytest tests/test_implied_vol.py
"""

from .black_scholes import bs_price


def implied_vol(price: float, S: float, K: float, T: float, r: float,
                kind: str = "call", tol: float = 1e-6, max_iter: int = 200) -> float:
    """Find sigma such that bs_price(S, K, T, r, sigma, kind) == price.

    Use bisection on sigma in [1e-4, 5.0]:

      1. First check the target is bracketed: price must be between
         bs_price(..., 1e-4) and bs_price(..., 5.0). If not, raise ValueError
         with a useful message — the quoted price violates no-arbitrage bounds
         (happens constantly with real stale quotes; your solver should say so
         rather than silently return garbage).
      2. Repeatedly halve the interval, keeping the half where the price
         function crosses the target. Vega > 0 means price is monotonically
         increasing in sigma, which is what makes bisection valid here.
      3. Stop when the interval is narrower than tol or max_iter is hit.

    Bisection gains one binary digit per iteration — slow but it cannot fail
    on a bracketed monotone function. Newton's method
    (sigma_next = sigma - (bs(sigma) - target) / vega(sigma)) converges
    quadratically but overshoots where vega is tiny (deep ITM/OTM, short
    expiry). Stretch goal: implement Newton with a bisection fallback and
    count iterations for both across a grid of moneyness.
    """
    raise NotImplementedError("Milestone 5")
