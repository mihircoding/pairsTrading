# Project 4 — Limit Order Book & Matching Engine

Build the data structure at the center of every modern exchange: a limit order book with
price-time priority, and the matching engine that crosses incoming orders against it.
Then simulate random order flow through it and watch bid-ask spreads and price impact
emerge from the mechanics.

This is the most "pure software engineering" project in the repo — no statistics, just
careful data-structure work with exact, testable rules. It's also the domain knowledge
that separates quant-dev candidates who have only seen daily bars from ones who understand
how prices actually form. HFT and exchange-side interviews lean on this material hard.

## How a limit order book works

An exchange keeps two sorted queues per instrument:

- **Bids** — resting buy orders, best (highest) price first
- **Asks** — resting sell orders, best (lowest) price first

```
        ASKS (sellers)
        101.30  x 400
        101.20  x 250
        101.10  x 700     <- best ask
        ------- spread -------
        101.00  x 300     <- best bid
        100.90  x 550
        100.80  x 200
        BIDS (buyers)
```

Rules that define matching (these ARE the spec — the tests encode them):

1. **Price priority**: an incoming buy matches the *lowest* ask first; an incoming sell
   matches the *highest* bid first.
2. **Time priority (FIFO)**: among resting orders at the same price, the oldest fills
   first. This is why co-location and latency matter — queue position is worth money.
3. **A limit order** rests in the book at its price *unless* it crosses the opposite
   side (a buy limit priced at or above the best ask executes immediately — a
   "marketable limit").
4. **A market order** takes whatever is on the other side, walking through price levels
   until filled (or the book runs dry).
5. **Partial fills**: an incoming order larger than the best resting order consumes it,
   then moves to the next order at that price, then to the next price level. Whatever
   remains of a limit order rests; the unfilled remainder of a market order is discarded.
6. **Trades print at the resting order's price** (the maker's price, not the taker's
   limit).

Vocabulary worth using correctly in interviews: the resting order is the **maker**
(supplies liquidity), the incoming order is the **taker** (consumes it). The spread is
the market maker's compensation for adverse selection; depth is how much size sits near
the top of the book; **price impact** is how far your order moves the price by eating
levels.

## Repo layout

```
04-limit-order-book/
├── README.md
├── requirements.txt
├── run_simulation.py       # random order flow through your book
├── src/
│   ├── order.py            # Order/Trade types (complete)
│   ├── orderbook.py        # TODO: the book + matching engine
│   └── simulator.py        # TODO: random order-flow generator
└── tests/
    ├── test_orderbook.py   # the matching spec, as executable scenarios
    └── test_simulator.py
```

## Build it: milestones

**Milestone 1 — Resting orders and best quotes** (`src/orderbook.py`)
`add_limit_order` for orders that don't cross: store them; implement `best_bid`,
`best_ask`, `depth`. Data structure choice is the interesting decision — the docstring
discusses dict-of-deques vs sorted structures and the real-world answer (price-bucketed
FIFO queues).

**Milestone 2 — Matching** (`add_limit_order` for crossing orders)
The core. Walk the opposite side price level by price level, oldest order first, filling
until the incoming order is exhausted or no longer crosses. Emit a `Trade` per fill at
the maker's price. Rest any remainder. The tests are a battery of exact scenarios —
partial fills, multi-level sweeps, time priority among equals.

**Milestone 3 — Market orders and cancels**
`market_order(side, qty)`: like matching, but no limit price to stop at (stop when the
book is empty). `cancel(order_id)`: remove a resting order — O(1) lookup via an id→order
map is the standard trick; lazy deletion (mark dead, skip when matching) is the
production-grade version.

**Milestone 4 — Order flow simulation** (`src/simulator.py`)
Generate random flow: limit orders placed near the mid, market orders, cancels of random
resting orders. Track the mid-price and spread over time. Even this crude "zero
intelligence" flow (agents with no strategy at all) reproduces real phenomena — spreads
that widen when depth thins, price impact from large market orders. That emergence is
the punchline of the project.

## Pitfalls checklist

- Trades printing at the taker's limit price instead of the maker's resting price.
- Time priority broken by using a dict/set where insertion order isn't the fill order —
  or by re-sorting a price level.
- A marketable limit that should PARTIALLY rest: buy 500 limit 101.10 against 300 resting
  at 101.10 → 300 fills, 200 rests as the new best bid... at 101.10, which was the ask
  price a moment ago. Get this scenario right and most others follow.
- Float prices as dict keys (0.1+0.2 problem). Real systems use integer ticks. The
  template keeps floats for readability but rounds to the tick — see the docstring.
- Crossing your own book in the simulator (self-trade) — real venues prevent it; at
  minimum know it's a thing.

## Stretch goals

- Iceberg orders (only part of the size is visible) and stop orders.
- Book snapshots: reconstruct the top-5-levels view after every event, like an exchange
  feed. Then compute realized spread and depth statistics from your simulation.
- Replay real messages: LOBSTER (https://lobsterdata.com/info/DataSamples.php) provides
  free sample files of real NASDAQ order-level data — parse and replay them through your
  book and check your reconstructed quotes against their book files.
- Benchmark: how many messages/second can your book process? Profile it, find the
  bottleneck, fix it once.

## Resources

- Larry Harris, *Trading and Exchanges* — THE market-microstructure book; part II
  explains every order type and who uses them and why.
- Gould et al. (2013), "Limit Order Books" — a thorough academic survey, free on arXiv:
  https://arxiv.org/abs/1012.0349
- LOBSTER sample data (real order-level NASDAQ data): https://lobsterdata.com
- CME's documentation of its matching algorithms (FIFO vs pro-rata) — real exchanges
  don't all use pure FIFO; worth knowing: search "CME matching algorithms".
- Databento's microstructure guides are practical and modern:
  https://databento.com/docs (see the knowledge-base articles).
