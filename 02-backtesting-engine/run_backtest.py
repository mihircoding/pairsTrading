"""Driver: run the MA-cross strategy through the engine on synthetic data.

Synthetic data on purpose — a trending sine wave makes it obvious whether the
strategy is doing what you think (long the upswings, flat the downswings).
Debug the machinery on data where you know the answer, then point the engine
at real prices (reuse src/data.py from project 01).

Usage:  python run_backtest.py   (after Milestones 1-4 are done)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data_handler import HistoricalDataHandler
from src.engine import Backtest
from src.execution import SimulatedExecutionHandler
from src.portfolio import Portfolio
from src.strategy import MovingAverageCrossStrategy


def make_prices(n: int = 500, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    path = 100 + 0.03 * t + 8 * np.sin(t / 25) + np.cumsum(rng.normal(0, 0.4, n))
    idx = pd.bdate_range("2023-01-01", periods=n)
    return pd.DataFrame({"SYN": path}, index=idx)


def main() -> None:
    data = HistoricalDataHandler(make_prices())
    strategy = MovingAverageCrossStrategy(data, short_window=10, long_window=30)
    portfolio = Portfolio(data, initial_cash=100_000.0, trade_size=500)
    execution = SimulatedExecutionHandler(data, slippage_bps=2.0,
                                          commission_per_share=0.005)

    equity = Backtest(data, strategy, portfolio, execution).run()

    total_ret = equity.iloc[-1] / equity.iloc[0] - 1
    daily = equity.pct_change().dropna()
    sharpe = daily.mean() / daily.std(ddof=1) * np.sqrt(252) if daily.std() > 0 else 0
    print(f"Final equity : {equity.iloc[-1]:,.2f}")
    print(f"Total return : {total_ret:+.2%}")
    print(f"Sharpe       : {sharpe:.2f}")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    data.prices["SYN"].plot(ax=axes[0], title="Synthetic price")
    equity.plot(ax=axes[1], title="Strategy equity")
    plt.tight_layout()
    plt.savefig("engine_backtest.png", dpi=120)
    print("Saved plot to engine_backtest.png")


if __name__ == "__main__":
    main()
