"""Black-Scholes closed-form price and analytic Greeks.

Milestones 1-2. Verify with:  pytest tests/test_black_scholes.py

Conventions used across the whole project:
    S     : spot price
    K     : strike
    T     : time to expiry in YEARS
    r     : continuously-compounded risk-free rate, annualized (0.05 = 5%)
    sigma : volatility, annualized (0.2 = 20%)
    kind  : "call" or "put"
"""

import numpy as np
from scipy.stats import norm


def _d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> tuple[float, float]:
    """Helper — implement first, both milestones need it.

    d1 = (ln(S/K) + (r + sigma^2 / 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    """
    raise NotImplementedError("Milestone 1")


def bs_price(S: float, K: float, T: float, r: float, sigma: float,
             kind: str = "call") -> float:
    """Milestone 1: European option price.

    call = S*N(d1) - K*exp(-r*T)*N(d2)
    put  = K*exp(-r*T)*N(-d2) - S*N(-d1)

    Edge case to handle BEFORE the formula: if T <= 0, return intrinsic value
    (max(S-K, 0) for a call, max(K-S, 0) for a put) — otherwise you divide by
    zero in d1.

    N is scipy.stats.norm.cdf.
    """
    raise NotImplementedError("Milestone 1")


def bs_greeks(S: float, K: float, T: float, r: float, sigma: float,
              kind: str = "call") -> dict:
    """Milestone 2: analytic Greeks. Return
    {'delta', 'gamma', 'vega', 'theta', 'rho'}.

    With phi = norm.pdf (the density, not the CDF!):

      delta_call = N(d1)                 delta_put = N(d1) - 1
      gamma      = phi(d1) / (S * sigma * sqrt(T))          (same for both)
      vega       = S * phi(d1) * sqrt(T)                    (same for both)
      theta_call = -S*phi(d1)*sigma/(2*sqrt(T)) - r*K*exp(-r*T)*N(d2)
      theta_put  = -S*phi(d1)*sigma/(2*sqrt(T)) + r*K*exp(-r*T)*N(-d2)
      rho_call   =  K*T*exp(-r*T)*N(d2)
      rho_put    = -K*T*exp(-r*T)*N(-d2)

    Conventions (documented so the tests are unambiguous):
      - vega is per unit of sigma (so vega/100 = change per vol point)
      - theta is per YEAR (theta/365 = per calendar day)
    """
    raise NotImplementedError("Milestone 2")


def fd_greek(pricer, greek: str, S: float, K: float, T: float, r: float,
             sigma: float, kind: str = "call", h: float = 1e-4) -> float:
    """Milestone 2 (second half): finite-difference Greeks.

    Central differences — bump the relevant input down and up, reprice, slope:

      delta ≈ (V(S+h) - V(S-h)) / (2h)          with h scaled: h_S = S * h
      gamma ≈ (V(S+h) - 2V(S) + V(S-h)) / h^2   (second difference)
      vega  ≈ (V(sigma+h) - V(sigma-h)) / (2h)
      theta ≈ -(V(T+h) - V(T-h)) / (2h)          (note the sign: decay)
      rho   ≈ (V(r+h) - V(r-h)) / (2h)

    `pricer` is passed in (use bs_price) so this same function can later
    difference your binomial or Monte Carlo pricers — that's the point of
    finite differences: they work on any model, including ones with no
    closed-form Greeks.
    """
    raise NotImplementedError("Milestone 2")
