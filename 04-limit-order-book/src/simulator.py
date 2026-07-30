"""Zero-intelligence order flow through the book.

Milestone 4. Verify with:  pytest tests/test_simulator.py

"Zero intelligence" (Gode & Sunder, 1993): agents submit random orders with no
strategy whatsoever. The remarkable result is how much realistic market
behavior — spreads, depth profiles, price impact — emerges from the matching
mechanics alone. If your simulated book behaves like a real one, the realism
was in the exchange rules, not the traders.
"""

import numpy as np

from .order import Side, to_tick
from .orderbook import LimitOrderBook


def seed_book(book: LimitOrderBook, mid: float = 100.0, levels: int = 5,
              qty: int = 100) -> None:
    """Complete. Pre-load `levels` price levels either side of `mid` so the
    simulation doesn't start from an empty (undefined-mid) book."""
    for i in range(1, levels + 1):
        book.add_limit_order(Side.BUY, to_tick(mid - 0.01 * i), qty)
        book.add_limit_order(Side.SELL, to_tick(mid + 0.01 * i), qty)


def simulate(book: LimitOrderBook, n_events: int = 5000, seed: int = 0) -> dict:
    """Milestone 4: push random events through the book, record what happens.

    Each event (draw with rng = np.random.default_rng(seed)):
      - 60%: LIMIT order. Random side. Price = current mid +/- an offset drawn
        from ~ |N(0, 3 ticks)|, placed passively (buys below mid, sells above)
        ~80% of the time and aggressively (crossing) the rest.
      - 25%: MARKET order, random side, qty ~ uniform 10..200.
      - 15%: CANCEL a uniformly-random resting order id (track live ids
        yourself; cancel() returning False for stale ids is fine and realistic).

    After each event record mid_price() and spread() (skip Nones when a side
    is momentarily empty).

    Return {'mids': list, 'spreads': list, 'n_trades': int, 'volume': int}.

    Things worth looking at in the output (put plots in your write-up):
      - The mid follows a random walk — no trader intent, still wanders.
      - Spread distribution: what widens it? (Depth getting eaten faster than
        it refills.)
      - Bigger market orders move the mid more — measure impact vs order size
        and you've reproduced a stylized fact of real markets.
    """
    raise NotImplementedError("Milestone 4")
