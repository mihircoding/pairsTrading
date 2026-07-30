"""The limit order book and matching engine.

Milestones 1-3. Verify with:  pytest tests/test_orderbook.py

Suggested internal representation (what most first implementations converge to):

    self.bids : dict[float, deque[Order]]   # price -> FIFO queue of resting orders
    self.asks : dict[float, deque[Order]]
    self._by_id : dict[int, Order]          # for O(1) cancel lookup
    self._next_ts : int                     # monotonically increasing sequence no.

A deque per price level gives you time priority for free (append to the back,
fill from the front). Finding the best price is then max(bids)/min(asks) over
the dict keys — O(number of price levels), which is fine here. Production books
keep a sorted structure (or an array indexed by tick) so best-price lookup is
O(1); that's a profiling-driven stretch goal, not where you start.
"""

from .order import Order, Side, Trade


class LimitOrderBook:
    def __init__(self):
        self.bids: dict[float, object] = {}
        self.asks: dict[float, object] = {}
        self._by_id: dict[int, Order] = {}
        self._next_ts = 0
        self._next_id = 0

    # ---------- Milestone 1: quotes ----------

    def best_bid(self) -> float | None:
        """Highest bid price with resting size, or None if no bids."""
        raise NotImplementedError("Milestone 1")

    def best_ask(self) -> float | None:
        """Lowest ask price with resting size, or None if no asks."""
        raise NotImplementedError("Milestone 1")

    def depth(self, side: Side, levels: int = 5) -> list[tuple[float, int]]:
        """Top `levels` price levels on one side as [(price, total_qty), ...],
        best first. Sum the quantities of every order resting at each price."""
        raise NotImplementedError("Milestone 1")

    # ---------- Milestones 1+2: limit orders ----------

    def add_limit_order(self, side: Side, price: float, quantity: int) -> tuple[int, list[Trade]]:
        """Submit a limit order. Returns (order_id, trades).

        Milestone 1 (non-crossing case): if the order does not cross the
        opposite side (a buy priced below the best ask, or the book is empty),
        wrap it in an Order (assign ids/timestamps from the counters) and
        append it to the FIFO queue at its price level. No trades.

        Milestone 2 (crossing case): while the order still crosses
        (buy: price >= best_ask; sell: price <= best_bid) and has quantity left:
          1. Take the FRONT order of the queue at the best opposite price
             (oldest first — time priority).
          2. fill = min(incoming remaining, resting order's quantity)
          3. Emit Trade(price=resting.price, quantity=fill, ...) — the MAKER's
             price, always.
          4. Reduce both quantities; if the resting order hits zero, pop it
             (and clean up: empty deque -> delete the price level, drop from
             _by_id).
        Anything left over rests in the book exactly like the non-crossing case.

        Keep this method the ONLY place matching logic lives — market orders
        (Milestone 3) are the same loop without the price condition, so factor
        the inner loop into a private helper you can share.
        """
        raise NotImplementedError("Milestone 1/2")

    # ---------- Milestone 3: market orders and cancels ----------

    def market_order(self, side: Side, quantity: int) -> list[Trade]:
        """Fill against the opposite side until done or the book is empty.
        Unfilled remainder is discarded (there is no price to rest at).
        Returns the trades."""
        raise NotImplementedError("Milestone 3")

    def cancel(self, order_id: int) -> bool:
        """Remove a resting order. True if found and removed, False otherwise
        (already filled, already cancelled, or never existed).

        _by_id gets you the Order in O(1); removing it from the middle of its
        deque is O(level size). Production trick worth knowing (and a fine
        stretch goal): LAZY deletion — flag the order dead here, and have the
        matching loop skip dead orders when they reach the front."""
        raise NotImplementedError("Milestone 3")

    # ---------- convenience (complete) ----------

    def mid_price(self) -> float | None:
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return (bb + ba) / 2

    def spread(self) -> float | None:
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return ba - bb
