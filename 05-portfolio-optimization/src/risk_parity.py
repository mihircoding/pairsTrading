"""Robust alternatives: shrinkage and risk-based weighting.

Milestone 5. Verify with:  pytest tests/test_risk_parity.py
"""

import numpy as np


def shrink_covariance(sample_cov: np.ndarray, alpha: float) -> np.ndarray:
    """Shrink the sample covariance toward its own diagonal.

    target = diag(sample_cov)  (as a full matrix: variances kept, correlations
                                zeroed)
    shrunk = (1 - alpha) * sample_cov + alpha * target

    alpha in [0, 1]: 0 = raw sample, 1 = fully diagonal. Ledoit-Wolf derive the
    optimal alpha analytically — compare yours against
    sklearn.covariance.LedoitWolf on real data as a stretch goal.
    """
    raise NotImplementedError("Milestone 5")


def inverse_vol_weights(cov: np.ndarray) -> np.ndarray:
    """w_i proportional to 1 / vol_i, normalized to sum to 1.

    The crude risk-parity: ignores correlations entirely. One line with numpy.
    """
    raise NotImplementedError("Milestone 5")


def risk_contributions(w: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """Each asset's share of total portfolio variance. Sums to 1.

    marginal_i = (cov @ w)_i          # d(variance)/d(w_i), up to a factor 2
    rc_i       = w_i * marginal_i / (w @ cov @ w)

    This decomposition is exact (Euler's theorem — variance is homogeneous of
    degree 2 in w). It's THE risk-report number: "asset X is 4% of the book but
    38% of the risk" is this quantity.
    """
    raise NotImplementedError("Milestone 5")


def equal_risk_contribution_weights(cov: np.ndarray) -> np.ndarray:
    """Weights where every asset contributes equally: rc_i = 1/n for all i.

    No closed form (except when all correlations are equal — then it's
    inverse-vol). Solve numerically; the standard trick is minimizing

        sum_i sum_j (rc_i - rc_j)^2

    subject to sum(w) = 1, w >= 0, with the scipy setup from optimizer.py.
    Start from inverse-vol weights — it's close to the answer and keeps SLSQP
    out of trouble.
    """
    raise NotImplementedError("Milestone 5")
