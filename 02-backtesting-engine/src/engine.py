"""The event loop that wires everything together.

Milestone 4. Verify with:  pytest tests/test_engine.py
"""

import queue

import pandas as pd

from .data_handler import HistoricalDataHandler
from .events import FillEvent, MarketEvent, OrderEvent, SignalEvent


class Backtest:
    def __init__(self, data: HistoricalDataHandler, strategy, portfolio, execution):
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution = execution
        self.events: queue.Queue = queue.Queue()

    def run(self) -> pd.Series:
        """Milestone 4: the main loop. Returns the equity curve.

        Pseudocode:

            while data.has_more():
                market_event = data.next_bar()
                events.put(market_event)

                while events not empty:
                    event = events.get()
                    if MarketEvent:
                        for each signal in strategy.on_market(event): put it
                    elif SignalEvent:
                        order = portfolio.on_signal(event)
                        if order is not None: put it
                    elif OrderEvent:
                        put execution.execute(event)
                    elif FillEvent:
                        portfolio.on_fill(event)

                portfolio.mark_to_market(data.current_time())   # AFTER the inner loop

            return pd.Series(dict(portfolio.equity_history))

        Notes:
          - Use isinstance() for dispatch; match/case on type works too.
          - mark_to_market must run after the inner while-loop so the bar's
            fills are reflected in that bar's equity. The end-to-end test
            checks the equity curve to the cent and will catch it if not.
          - queue.Queue.empty() is fine here (single thread).
        """
        raise NotImplementedError("Milestone 4")
