"""Driver: seed the book, run random flow, plot what emerges.

Usage:  python run_simulation.py   (after Milestones 1-4 are done)
"""

import matplotlib.pyplot as plt

from src.orderbook import LimitOrderBook
from src.simulator import seed_book, simulate


def main() -> None:
    book = LimitOrderBook()
    seed_book(book, mid=100.0, levels=5, qty=100)
    result = simulate(book, n_events=20_000, seed=7)

    print(f"Trades executed : {result['n_trades']:,}")
    print(f"Volume traded   : {result['volume']:,}")
    print(f"Final mid       : {result['mids'][-1]:.2f}")
    avg_spread = sum(result["spreads"]) / len(result["spreads"])
    print(f"Average spread  : {avg_spread:.4f}")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(result["mids"], lw=0.7)
    axes[0].set_title("Mid price — a random walk born from random flow")
    axes[1].plot(result["spreads"], lw=0.5)
    axes[1].set_title("Bid-ask spread")
    plt.tight_layout()
    plt.savefig("simulation.png", dpi=120)
    print("Saved plot to simulation.png")


if __name__ == "__main__":
    main()
