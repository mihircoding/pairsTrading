"""Pair selection: hedge ratios and cointegration testing.

Milestones 1-3. Implement the three functions below, in order.
Verify with:  pytest tests/test_pairs.py
"""

from itertools import combinations

import pandas as pd


def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """Milestone 1: OLS hedge ratio of y on x.

    Fit y = alpha + beta * x by ordinary least squares and return beta.

    Hints:
      - statsmodels: sm.OLS(y, sm.add_constant(x)).fit() — beta is in .params
      - or do it with numpy: np.polyfit(x, y, 1) gives you [slope, intercept]
      - don't forget the intercept; forcing the line through zero biases beta

    Why it matters: beta is the number of shares of x you hold against each
    share of y so that the combined position is (historically) stationary.
    """
    raise NotImplementedError("Milestone 1")


def engle_granger_pvalue(y: pd.Series, x: pd.Series) -> float:
    """Milestone 2: Engle-Granger cointegration test. Return the ADF p-value.

    Steps:
      1. beta = hedge_ratio(y, x)   (reuse Milestone 1)
      2. spread = y - beta * x
      3. Run an Augmented Dickey-Fuller test on the spread:
         statsmodels.tsa.stattools.adfuller(spread) -> the p-value is element [1]
      4. Return that p-value.

    Interpretation: small p-value (< 0.05) => reject "spread is a random walk"
    => the spread is stationary => the pair is cointegrated.

    Sanity check: statsmodels.tsa.stattools.coint(y, x) does roughly this in one
    call (with slightly different critical values). Compare your output to it.
    """
    raise NotImplementedError("Milestone 2")


def find_cointegrated_pairs(
    prices: pd.DataFrame,
    max_pvalue: float = 0.05,
) -> pd.DataFrame:
    """Milestone 3: scan every ticker pair, keep the cointegrated ones.

    For each unordered pair of columns in `prices`, compute the Engle-Granger
    p-value and the hedge ratio. Return a DataFrame with columns
    ['a', 'b', 'pvalue', 'beta'], containing only rows with pvalue <= max_pvalue,
    sorted by pvalue ascending.

    Hints:
      - itertools.combinations(prices.columns, 2) enumerates the pairs
      - build a list of dicts, then pd.DataFrame(rows)

    Think about (and mention in your write-up): with n tickers you run
    n*(n-1)/2 tests. At a 5% threshold, how many "cointegrated" pairs do you
    expect to find in pure noise? This is the multiple-comparisons problem.
    """
    raise NotImplementedError("Milestone 3")
