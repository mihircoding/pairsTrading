"""Driver: the full pipeline on a real ETF universe.

ETFs rather than single stocks: they're diversified already, so the covariance
structure is stable enough for the differences between methods to be visible
rather than drowned in noise.

Usage:  python run_optimization.py   (after Milestones 1-5 are done)
"""

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf

from src.frontier import efficient_frontier
from src.optimizer import max_sharpe_weights, min_variance_weights, portfolio_performance
from src.returns import annualized_cov, annualized_mean
from src.risk_parity import equal_risk_contribution_weights, risk_contributions

# stocks / intl stocks / bonds / gold / real estate — deliberately heterogeneous
UNIVERSE = ["SPY", "EFA", "AGG", "GLD", "VNQ"]
START, END = "2018-01-01", "2024-12-31"


def main() -> None:
    prices = yf.download(UNIVERSE, start=START, end=END, auto_adjust=True,
                         progress=False)["Close"].dropna()
    mu = annualized_mean(prices).values
    cov = annualized_cov(prices).values

    portfolios = {
        "Equal weight": np.full(len(UNIVERSE), 1 / len(UNIVERSE)),
        "Min variance": min_variance_weights(cov),
        "Max Sharpe": max_sharpe_weights(mu, cov),
        "Equal risk contribution": equal_risk_contribution_weights(cov),
    }

    print(f"{'portfolio':<26} {'ret':>7} {'vol':>7} {'sharpe':>7}   weights")
    for name, w in portfolios.items():
        ret, vol, sharpe = portfolio_performance(w, mu, cov)
        ws = " ".join(f"{t}:{x:.0%}" for t, x in zip(UNIVERSE, w))
        print(f"{name:<26} {ret:>7.2%} {vol:>7.2%} {sharpe:>7.2f}   {ws}")

    print("\nRisk contributions (compare Max Sharpe vs ERC — this is the point):")
    for name in ("Max Sharpe", "Equal risk contribution"):
        rc = risk_contributions(portfolios[name], cov)
        print(f"  {name:<26} " + " ".join(f"{t}:{x:.0%}" for t, x in zip(UNIVERSE, rc)))

    ef = efficient_frontier(mu, cov, n_points=40)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(ef["volatility"], ef["target_return"], "-", label="efficient frontier")
    for name, w in portfolios.items():
        ret, vol, _ = portfolio_performance(w, mu, cov)
        ax.scatter(vol, ret, label=name, zorder=3)
    ax.set_xlabel("Volatility (ann.)"); ax.set_ylabel("Expected return (ann.)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("frontier.png", dpi=120)
    print("\nSaved plot to frontier.png")


if __name__ == "__main__":
    main()
