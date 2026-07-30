"""End-to-end driver: scan for pairs on one period, trade them on a later one.

This script won't run until Milestones 1-5 are implemented. It exists so you can
see the intended shape of the whole pipeline before you start.

Usage:  python run_backtest.py
"""

import matplotlib.pyplot as plt

from src.backtest import backtest_pair, summarize
from src.data import load_prices
from src.pairs import find_cointegrated_pairs, hedge_ratio
from src.signals import compute_spread, generate_positions, rolling_zscore

# A small universe of plausibly-related names. Deliberately includes sector
# clusters (banks, oil, exchanges) where economic linkage is believable —
# scanning random tickers mostly finds statistical accidents.
UNIVERSE = ["XOM", "CVX", "COP", "JPM", "BAC", "WFC", "GS", "MS", "ICE", "CME", "V", "MA"]

FORMATION = ("2018-01-01", "2021-12-31")  # find pairs here
TRADING = ("2022-01-01", "2024-12-31")    # trade them here (out of sample!)


def main() -> None:
    print("Downloading formation window...")
    formation_prices = load_prices(UNIVERSE, *FORMATION)

    print("Scanning for cointegrated pairs...")
    pairs = find_cointegrated_pairs(formation_prices, max_pvalue=0.05)
    print(pairs.head(10).to_string(index=False))
    if pairs.empty:
        print("No pairs passed. Loosen max_pvalue or widen the universe.")
        return

    best = pairs.iloc[0]
    a, b = best["a"], best["b"]
    print(f"\nTrading {a}/{b} on the out-of-sample window...")

    trading_prices = load_prices([a, b], *TRADING)
    y, x = trading_prices[a], trading_prices[b]

    # Re-estimate beta on formation data only — using the trading window would
    # leak future information into the hedge ratio.
    beta = hedge_ratio(formation_prices[a], formation_prices[b])

    spread = compute_spread(y, x, beta)
    z = rolling_zscore(spread, window=60)
    pos = generate_positions(z, entry=2.0, exit=0.5)
    result = backtest_pair(y, x, beta, pos, cost_bps=5.0)

    stats = summarize(result, pos)
    print(f"\n{a}/{b}  beta={beta:.2f}")
    for k, v in stats.items():
        print(f"  {k:>15}: {v:.4f}" if isinstance(v, float) else f"  {k:>15}: {v}")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    z.plot(ax=axes[0], title=f"{a}/{b} rolling z-score")
    axes[0].axhline(2, ls="--", c="gray"); axes[0].axhline(-2, ls="--", c="gray")
    result["equity"].plot(ax=axes[1], title="Equity curve (net of costs)")
    plt.tight_layout()
    plt.savefig("backtest.png", dpi=120)
    print("\nSaved plot to backtest.png")


if __name__ == "__main__":
    main()
