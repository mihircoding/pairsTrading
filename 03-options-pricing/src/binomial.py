"""Cox-Ross-Rubinstein binomial tree.

Milestone 3. Verify with:  pytest tests/test_binomial.py
"""

import numpy as np


def crr_price(S: float, K: float, T: float, r: float, sigma: float,
              kind: str = "call", steps: int = 500, american: bool = False) -> float:
    """Price an option on a recombining binomial tree.

    Setup (CRR parameterization):
        dt = T / steps
        u  = exp(sigma * sqrt(dt))      # up factor
        d  = 1 / u                      # down factor (recombining!)
        p  = (exp(r*dt) - d) / (u - d)  # risk-neutral up probability
        disc = exp(-r * dt)

    Algorithm:
      1. Terminal stock prices: S * u^j * d^(steps-j) for j = 0..steps.
         (numpy: build the whole vector at once, no loops needed here)
      2. Terminal option values: payoff of each terminal price.
      3. Roll backwards one step at a time:
             value = disc * (p * value_up + (1-p) * value_down)
         In vector terms, at each step the value array shrinks by one:
             value = disc * (p * value[1:] + (1 - p) * value[:-1])
      4. If american=True: at each step, also recompute the stock prices at
         that layer and take max(continuation, immediate exercise payoff).
         This one line is the entire difference between European and American
         pricing — and it's why there's no Black-Scholes formula for American
         puts (the exercise decision is embedded in the recursion).
      5. After `steps` rollbacks, value has one element: the price.

    Sanity anchors the tests use:
      - European prices converge to Black-Scholes as steps -> infinity
        (CRR error shrinks roughly like 1/steps).
      - American call on a non-dividend stock == European call (never optimal
        to exercise early). American put > European put.
    """
    raise NotImplementedError("Milestone 3")
