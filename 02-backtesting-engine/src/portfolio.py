"""Position/cash accounting, order sizing, and the equity curve.

Milestone 2. Verify with:  pytest tests/test_portfolio.py

State you need to maintain:
    cash      : float, starts at initial_cash
    positions : dict symbol -> signed share count (missing key == 0)
    equity    : list of (time, total_equity) recorded once per bar
"""

from .data_handler import HistoricalDataHandler
from .events import OrderEvent, SignalEvent, SignalType


class Portfolio:
    def __init__(self, data: HistoricalDataHandler, initial_cash: float = 100_000.0,
                 trade_size: int = 100):
        self.data = data
        self.initial_cash = initial_cash
        self.trade_size = trade_size
        self.cash = initial_cash
        self.positions: dict[str, int] = {}
        self.equity_history: list[tuple] = []

    def on_signal(self, signal: SignalEvent) -> OrderEvent | None:
        """Milestone 2a: turn an opinion into a sized order (or None).

        Fixed-size scheme (deliberately simple — sizing is a project of its own):
          LONG  -> target position = +trade_size
          SHORT -> target position = -trade_size
          EXIT  -> target position = 0

        Emit an order for the DIFFERENCE between target and current position.
        If the difference is zero (already there), return None — don't spam
        zero-quantity orders.
        """
        raise NotImplementedError("Milestone 2")

    def on_fill(self, fill) -> None:
        """Milestone 2b: update cash and positions from a FillEvent.

        cash -= fill.quantity * fill.fill_price   (buys cost cash, sells add it;
                                                   the sign handles both cases)
        cash -= fill.commission                    (always a cost)
        positions[symbol] += fill.quantity

        No other bookkeeping. Resist the urge to track P&L here — equity is
        computed from cash + marked positions, which cannot drift out of sync.
        """
        raise NotImplementedError("Milestone 2")

    def total_equity(self) -> float:
        """Milestone 2c: cash + sum over positions of (shares * current price).

        Uses self.data.current_price(symbol) to mark each position.
        """
        raise NotImplementedError("Milestone 2")

    def mark_to_market(self, time) -> None:
        """Milestone 2d: append (time, total_equity()) to equity_history.

        The engine calls this once per bar, AFTER all of that bar's events are
        processed. Called before fills, your equity curve lags reality — a
        classic ordering bug the engine test will catch.
        """
        raise NotImplementedError("Milestone 2")
