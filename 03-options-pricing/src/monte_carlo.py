"""Monte Carlo pricing under geometric Brownian motion.

Milestone 4. Verify with:  pytest tests/test_monte_carlo.py
"""

import numpy as np


def mc_price(S: float, K: float, T: float, r: float, sigma: float,
             kind: str = "call", n_paths: int = 200_000,
             seed: int | None = 0, antithetic: bool = False) -> tuple[float, float]:
    """Price a European option by simulation. Return (price, standard_error).

    For a European payoff you do NOT need to simulate day-by-day paths — GBM
    has an exact solution for the terminal price:

        S_T = S * exp((r - sigma^2/2) * T + sigma * sqrt(T) * Z),   Z ~ N(0,1)

    Steps:
      1. rng = np.random.default_rng(seed); draw Z, shape (n_paths,).
      2. Terminal prices S_T via the formula (one vectorized line).
      3. payoffs = max(S_T - K, 0) for calls, max(K - S_T, 0) for puts
         (np.maximum, not np.max).
      4. discounted = exp(-r*T) * payoffs
      5. price = discounted.mean()
         stderr = discounted.std(ddof=1) / sqrt(n_paths)

    The standard error is not optional. A Monte Carlo estimate is a sample
    mean; the CLT gives you its distribution; quoting it without the error bar
    is quoting a random number. The test literally checks
    |mc - black_scholes| < 3 * stderr.

    antithetic=True (stretch goal): for every Z also use -Z, and average each
    pair's payoff before computing the mean/stderr. Same cost, lower variance
    (the pairs are negatively correlated). Measure how much the stderr drops.
    """
    raise NotImplementedError("Milestone 4")
