# Project 2 — Event-Driven Backtesting Engine

Build a small event-driven backtester from scratch: the same architecture (in miniature)
that production trading systems use. This is the most software-engineering-heavy project
in the repo, and the one most relevant to *quant developer* roles specifically — the job
is usually building and maintaining exactly this kind of infrastructure.

## Vectorized vs event-driven: why bother?

Project 1's backtest was **vectorized**: whole-series pandas operations, everything computed
at once. Vectorized backtests are fast and great for research, but they have structural
problems:

- It's easy to accidentally use future data (a whole column exists at once).
- Realistic order handling is awkward: partial fills, limit orders, stops, latency,
  position limits don't map to column arithmetic.
- The backtest code looks nothing like live trading code, so going live means a rewrite —
  and a fresh set of bugs.

An **event-driven** backtester processes one timestamp at a time through a queue of events,
exactly like a live system processes messages from an exchange feed. The strategy literally
*cannot* see the future because future bars haven't been fed in yet. And the same
strategy/portfolio/execution classes can later run live by swapping the data handler and
execution handler for real ones.

## The architecture

Five components, one queue. Each component consumes one event type and emits another:

```
DataHandler --MarketEvent--> Strategy --SignalEvent--> Portfolio
                                                          |
     Portfolio <--FillEvent-- ExecutionHandler <--OrderEvent
```

- **MarketEvent** — "a new bar arrived" (timestamp).
- **SignalEvent** — the strategy's *opinion*: long, short, or exit a symbol. No sizes.
- **OrderEvent** — the portfolio's *decision*: buy/sell N shares. Sizing and risk live here.
- **FillEvent** — what actually happened: executed quantity, price (with slippage), commission.

The separation matters. Strategies express views; the portfolio turns views into sized
orders (this is where risk management lives); the execution handler models market frictions.
In real shops these are separate systems owned by separate teams.

The engine is a loop:

```
for each timestamp in the data:
    push MarketEvent
    while the queue is not empty:
        event = queue.get()
        dispatch to whoever handles that event type
        (handlers may push new events onto the queue)
    portfolio.mark_to_market(timestamp)
```

## Repo layout

```
02-backtesting-engine/
├── README.md
├── requirements.txt
├── run_backtest.py          # driver: MA-cross on synthetic data
├── src/
│   ├── events.py            # event dataclasses (complete)
│   ├── data_handler.py      # replays bars, guards against lookahead (complete)
│   ├── strategy.py          # TODO: moving-average cross strategy
│   ├── portfolio.py         # TODO: sizing, cash/position accounting, equity
│   ├── execution.py         # TODO: fills with slippage + commission
│   └── engine.py            # TODO: the event loop
└── tests/
    ├── test_execution.py
    ├── test_portfolio.py
    ├── test_strategy.py
    └── test_engine.py
```

## Build it: milestones

**Milestone 1 — Execution handler** (`src/execution.py`)
Turn an OrderEvent into a FillEvent at the current price, worsened by slippage
(buys fill higher, sells fill lower) plus per-share commission. Simplest realistic model;
the docstring has the formulas.

**Milestone 2 — Portfolio** (`src/portfolio.py`)
The accounting heart. Track cash and positions; on a fill, update both (buys reduce cash
by qty*price + commission). On a signal, emit a sized order (fixed-size to start). At the
end of each bar, mark positions to market and record total equity. Most real-world
backtester bugs are accounting bugs — the tests are picky on purpose.

**Milestone 3 — Strategy** (`src/strategy.py`)
A moving-average crossover: long when the short MA is above the long MA, exit when it
drops below. Key discipline: the strategy may only call `data.get_latest(symbol, n)` —
the data handler physically won't give it unseen bars.

**Milestone 4 — The engine** (`src/engine.py`)
Wire it together with `queue.Queue`. Get the dispatch right: MarketEvent → strategy AND
portfolio (mark-to-market), SignalEvent → portfolio, OrderEvent → execution,
FillEvent → portfolio. The end-to-end test runs buy-and-hold through the full loop and
checks the final equity matches the asset's return to the cent.

**Milestone 5 — Run and extend**
`run_backtest.py` runs the MA cross on a synthetic trending series. Then extend:
limit orders, position limits, a short-selling check, multiple symbols, a
stop-loss — each is a small, well-contained change, which is the point of the
architecture.

## Design details worth understanding (interview fodder)

- **Why a queue instead of direct method calls?** Decoupling: components only know about
  events, not each other. One SignalEvent may fan out into several OrderEvents; a fill
  arrives asynchronously in live trading. The queue makes the data flow explicit and
  identical between backtest and live.
- **Fill price realism**: filling at the same bar's close is optimistic (you saw the close,
  then traded at it). Filling at the *next bar's open* is more honest. We start with
  same-bar-close + slippage for simplicity — know this is a modeling choice and be able to
  defend it.
- **Float vs Decimal**: we use floats and round in tests. Real accounting systems use
  integer ticks/cents. Worth knowing why (0.1 + 0.2 != 0.3).

## Pitfalls checklist

- Marking equity before processing that bar's fills (order of operations in the loop).
- Letting the strategy peek at the full DataFrame instead of going through `get_latest`.
- Charging commission on the order rather than the fill (partial fills, in richer models).
- Signals on every bar instead of only on *crossings* — your portfolio then churns orders
  every bar and commissions eat everything. The strategy must track its own state.

## Resources

- QuantStart's "Event-Driven Backtesting with Python" series — the canonical free
  walkthrough of exactly this architecture: https://www.quantstart.com/articles/
- Backtrader and Zipline (open-source event-driven backtesters) — read their source after
  building your own; you'll recognize every component:
  https://github.com/mementum/backtrader , https://github.com/quantopian/zipline
- Ernest Chan, *Quantitative Trading*, ch. 5 on backtesting pitfalls.
- Robert Pardo, *The Evaluation and Optimization of Trading Strategies* — walk-forward
  testing, when you're ready to get serious about overfitting.
