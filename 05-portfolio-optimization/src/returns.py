"""Return and covariance estimation.

Milestone 1. Verify with:  pytest tests/test_returns.py

Conventions everything downstream depends on:
  - simple daily returns:  r_t = P_t / P_{t-1} - 1   (pct_change, drop first NaN)
  - annualized mean return:      daily mean * 252
  - annualized covariance:       daily covariance * 252
  - annualized volatility:       daily std * sqrt(252)   <- sqrt! variance scales
                                                            with time, vol doesn't
"""

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns; first row (NaN) dropped."""
    raise NotImplementedError("Milestone 1")


def annualized_mean(prices: pd.DataFrame) -> pd.Series:
    """Annualized expected return per asset (mu vector)."""
    raise NotImplementedError("Milestone 1")


def annualized_cov(prices: pd.DataFrame) -> pd.DataFrame:
    """Annualized covariance matrix. Use sample covariance (pandas default,
    ddof=1)."""
    raise NotImplementedError("Milestone 1")
