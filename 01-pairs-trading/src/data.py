"""Price data download and caching.

This module is complete — read it to understand the data format the rest of the
project expects, but you shouldn't need to change it.

Everything downstream works on a single DataFrame:
    index   : DatetimeIndex (trading days)
    columns : ticker symbols
    values  : adjusted close prices (floats)

Yahoo Finance is free and fine for learning. Its adjusted closes are back-adjusted
for splits and dividends, which is what you want for return calculations. It is
NOT survivorship-bias-free and NOT suitable for anything real.
"""

from pathlib import Path

import pandas as pd

CACHE_DIR = Path(__file__).resolve().parent.parent / "data"


def load_prices(
    tickers: list[str],
    start: str,
    end: str,
    cache: bool = True,
) -> pd.DataFrame:
    """Download adjusted close prices, using a local CSV cache when possible.

    Caching matters: Yahoo rate-limits aggressively, and re-downloading the same
    data on every test run is slow and rude.
    """
    cache_file = CACHE_DIR / f"{'_'.join(sorted(tickers))}_{start}_{end}.csv"

    if cache and cache_file.exists():
        prices = pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        import yfinance as yf

        raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        prices = raw["Close"]
        if isinstance(prices, pd.Series):  # single ticker comes back as a Series
            prices = prices.to_frame(tickers[0])
        if cache:
            CACHE_DIR.mkdir(exist_ok=True)
            prices.to_csv(cache_file)

    # Drop days where any ticker is missing so every series is aligned.
    prices = prices.dropna(how="any")
    return prices
