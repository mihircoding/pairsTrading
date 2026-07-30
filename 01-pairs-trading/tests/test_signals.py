import numpy as np
import pandas as pd
import pytest

from src.signals import compute_spread, generate_positions, rolling_zscore


class TestSpread:
    def test_definition(self):
        y = pd.Series([10.0, 12.0, 14.0])
        x = pd.Series([2.0, 3.0, 4.0])
        expected = y - 1.5 * x
        pd.testing.assert_series_equal(compute_spread(y, x, 1.5), expected)


class TestRollingZscore:
    def test_no_lookahead(self, cointegrated_pair):
        """The z-score at time t must not change if the future changes."""
        y, x = cointegrated_pair
        spread = y - 2.5 * x
        z_full = rolling_zscore(spread, window=60)
        z_trunc = rolling_zscore(spread.iloc[:800], window=60)
        pd.testing.assert_series_equal(z_full.iloc[:800], z_trunc)

    def test_warmup_is_nan(self, cointegrated_pair):
        y, x = cointegrated_pair
        z = rolling_zscore(y - 2.5 * x, window=60)
        assert z.iloc[:59].isna().all()
        assert not np.isnan(z.iloc[59])

    def test_standardization(self, rng):
        """On stationary noise, the rolling z-score should be roughly N(0,1)."""
        s = pd.Series(rng.normal(5.0, 2.0, 3000))
        z = rolling_zscore(s, window=100).dropna()
        assert abs(z.mean()) < 0.1
        assert 0.8 < z.std() < 1.2


class TestPositions:
    def make_z(self, values):
        return pd.Series(values, dtype=float)

    def test_entry_and_exit_thresholds(self):
        #        flat   entry short      hold        exit    flat
        z = self.make_z([0.0, 2.5, 1.5, 1.0, 0.4, 0.0])
        pos = generate_positions(z, entry=2.0, exit=0.5)
        assert pos.tolist() == [0, -1, -1, -1, 0, 0]

    def test_long_side(self):
        z = self.make_z([0.0, -2.5, -1.0, -0.3, 0.0])
        pos = generate_positions(z, entry=2.0, exit=0.5)
        assert pos.tolist() == [0, 1, 1, 0, 0]

    def test_hysteresis_no_reentry_between_thresholds(self):
        """z between exit and entry when flat -> stay flat."""
        z = self.make_z([0.0, 1.5, 1.9, 1.0])
        pos = generate_positions(z, entry=2.0, exit=0.5)
        assert pos.tolist() == [0, 0, 0, 0]

    def test_nan_stays_flat(self):
        z = self.make_z([np.nan, np.nan, 2.5, 0.1])
        pos = generate_positions(z, entry=2.0, exit=0.5)
        assert pos.tolist() == [0, 0, -1, 0]
