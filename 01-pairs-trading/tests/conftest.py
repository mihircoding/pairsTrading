"""Shared synthetic fixtures.

Real market data is noisy and non-reproducible, so the tests use synthetic
series where the right answer is known by construction. This is also how you
should debug your own quant code: if it can't recover parameters you planted,
it can't be trusted on real data.
"""

import numpy as np
import pandas as pd
import pytest

N = 1500
SEED = 42


@pytest.fixture
def rng():
    return np.random.default_rng(SEED)


@pytest.fixture
def cointegrated_pair(rng):
    """A pair that is cointegrated by construction.

    x is a random walk; y = 10 + 2.5 * x + stationary AR(1) noise.
    The spread y - 2.5x is mean-reverting, so Engle-Granger should flag it.
    """
    idx = pd.bdate_range("2018-01-01", periods=N)
    x = pd.Series(100 + np.cumsum(rng.normal(0, 1, N)), index=idx, name="x")

    noise = np.zeros(N)
    for t in range(1, N):  # AR(1), phi=0.85 -> stationary
        noise[t] = 0.85 * noise[t - 1] + rng.normal(0, 1)
    y = pd.Series(10 + 2.5 * x.values + noise, index=idx, name="y")
    return y, x


@pytest.fixture
def independent_walks(rng):
    """Two unrelated random walks. NOT cointegrated."""
    idx = pd.bdate_range("2018-01-01", periods=N)
    a = pd.Series(100 + np.cumsum(rng.normal(0, 1, N)), index=idx, name="a")
    b = pd.Series(100 + np.cumsum(rng.normal(0, 1, N)), index=idx, name="b")
    return a, b
