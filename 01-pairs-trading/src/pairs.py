"""Pair selection: hedge ratio, Engle-Granger cointegration, and pair scanning.

Milestones 1-3. Verify with:  pytest tests/test_pairs.py
"""

from itertools import combinations

import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller


def _align(y: pd.Series, x: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Inner-join two series on their index and drop any row with a NaN.

    Every function here regresses one price series on another, and statsmodels
    will happily produce garbage (or raise) if the two are misaligned or carry
    NaNs. Doing the alignment once, here, keeps that concern out of the maths.
    """
    df = pd.concat([y, x], axis=1, join="inner").dropna()
    return df.iloc[:, 0], df.iloc[:, 1]


def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """Milestone 1: OLS hedge ratio of y on x.

    Fit y = alpha + beta * x by ordinary least squares and return beta.

    The intercept matters: two price series rarely share a level (one stock
    trades at $30, the other at $300), and forcing the line through the origin
    would push that level difference into the slope, biasing beta.

    Economically, beta is the number of shares of x you short against each
    share of y you hold so that the combined position is (historically)
    stationary.
    """
    y, x = _align(y, x)
    model = sm.OLS(y, sm.add_constant(x)).fit()
    # params = [const, slope]; take the slope positionally so this works
    # whether or not the input Series carry names.
    return float(model.params.iloc[1])


def engle_granger_pvalue(y: pd.Series, x: pd.Series) -> float:
    """Milestone 2: Engle-Granger cointegration test. Return the ADF p-value.

    Two steps:
      1. Regress y on x by OLS; the residual is the spread y - beta * x.
      2. ADF-test that spread. The ADF null hypothesis is "this series has a
         unit root", i.e. it is a random walk that never has to come back.

    A small p-value (< 0.05) rejects the null: the spread is stationary, the
    pair is cointegrated, and the spread is the thing you can actually trade.

    Note the asymmetry — engle_granger_pvalue(y, x) is not exactly
    engle_granger_pvalue(x, y), because OLS minimises error in the dependent
    variable only. The two p-values are usually close; when they disagree
    badly, that is itself evidence the relationship is weak.

    Caveat worth stating in an interview: because beta is *estimated* rather
    than known, the standard ADF critical values are slightly too permissive
    here. statsmodels' coint() uses Engle-Granger-specific critical values and
    is the stricter, more correct comparison; see tools/sanity_check.py.
    """
    y, x = _align(y, x)
    beta = hedge_ratio(y, x)
    spread = y - beta * x
    # regression="c": the spread has a nonzero mean (the OLS intercept), but no
    # trend — a trending spread would not be tradeable as a mean reverter.
    return float(adfuller(spread, regression="c", autolag="AIC")[1])


def find_cointegrated_pairs(
    prices: pd.DataFrame,
    max_pvalue: float = 0.05,
) -> pd.DataFrame:
    """Milestone 3: scan every ticker pair, keep the cointegrated ones.

    Returns a DataFrame with columns ['a', 'b', 'pvalue', 'beta'], filtered to
    pvalue <= max_pvalue and sorted by pvalue ascending. Column 'a' is the
    dependent leg, 'b' the independent one, and beta is the hedge ratio of a
    on b — so downstream code can do spread = a - beta * b directly.

    THE MULTIPLE-COMPARISONS PROBLEM (the reason this function is dangerous):
    with n tickers you run n*(n-1)/2 tests. For n=50 that is 1,225 tests, and
    a 5% threshold means ~61 pairs clear the bar *on pure noise alone*. Rank
    the survivors by p-value and the top of the list is disproportionately
    populated by lucky accidents, because you selected on the noise.

    Defences, roughly in order of how much they help:
      - Restrict the universe to economically linked names up front (two oil
        majors, two exchanges) so a passing test corroborates a prior story
        rather than inventing one.
      - Scan on a formation window and trade on a later window, so a pair has
        to survive out of sample.
      - Formally adjust the threshold (Bonferroni: max_pvalue / n_tests, or
        Benjamini-Hochberg for false-discovery-rate control).
    """
    rows = []
    for a, b in combinations(prices.columns, 2):
        y, x = prices[a], prices[b]
        rows.append(
            {
                "a": a,
                "b": b,
                "pvalue": engle_granger_pvalue(y, x),
                "beta": hedge_ratio(y, x),
            }
        )

    result = pd.DataFrame(rows, columns=["a", "b", "pvalue", "beta"])
    result = result[result["pvalue"] <= max_pvalue]
    return result.sort_values("pvalue").reset_index(drop=True)
