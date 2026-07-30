"""Strategies consume market data and emit signals.

Milestone 3. Verify with:  pytest tests/test_strategy.py
"""

from .data_handler import HistoricalDataHandler
from .events import MarketEvent, SignalEvent, SignalType


class BuyAndHoldStrategy:
    """Complete reference strategy: goes long each symbol once, on the first
    bar, then does nothing. Used by the end-to-end engine test. Read it to see
    the contract a strategy must follow."""

    def __init__(self, data: HistoricalDataHandler):
        self.data = data
        self._bought: set[str] = set()

    def on_market(self, event: MarketEvent) -> list[SignalEvent]:
        signals = []
        for symbol in self.data.symbols:
            if symbol not in self._bought:
                signals.append(SignalEvent(event.time, symbol, SignalType.LONG))
                self._bought.add(symbol)
        return signals


class MovingAverageCrossStrategy:
    """Milestone 3: long when short-MA > long-MA, exit when it crosses back.

    Implement on_market() so that it:
      1. For each symbol, pulls the last `long_window` closes via
         self.data.get_latest(symbol, self.long_window).
      2. If fewer than long_window bars exist yet, emits nothing (warmup).
      3. Computes short_ma (mean of last short_window closes) and long_ma
         (mean of all long_window closes).
      4. Emits LONG when short_ma > long_ma AND we are not already long;
         emits EXIT when short_ma <= long_ma AND we are currently long;
         otherwise emits nothing.

    That "AND we are not already long" is the important part: signal on the
    CROSSING, not the state. Track what you've signaled per symbol in
    self._in_position (a set). Without this, you emit LONG every single bar
    the MAs are apart, and the portfolio/commission model punishes you.
    """

    def __init__(self, data: HistoricalDataHandler, short_window: int = 10,
                 long_window: int = 30):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self._in_position: set[str] = set()

    def on_market(self, event: MarketEvent) -> list[SignalEvent]:
        raise NotImplementedError("Milestone 3")
