import pytest

from src.black_scholes import bs_price
from src.monte_carlo import mc_price

BASE = dict(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)


class TestMonteCarlo:
    @pytest.mark.parametrize("kind", ["call", "put"])
    def test_price_within_confidence_interval(self, kind):
        price, stderr = mc_price(**BASE, kind=kind, n_paths=200_000, seed=0)
        closed = bs_price(**BASE, kind=kind)
        assert stderr > 0
        assert abs(price - closed) < 3 * stderr

    def test_seed_reproducibility(self):
        a = mc_price(**BASE, seed=123)
        b = mc_price(**BASE, seed=123)
        assert a == b

    def test_stderr_shrinks_like_sqrt_n(self):
        _, se_small = mc_price(**BASE, n_paths=10_000, seed=1)
        _, se_large = mc_price(**BASE, n_paths=160_000, seed=1)
        # 16x the paths -> ~4x smaller stderr (allow slack for noise)
        assert se_large < se_small / 3.0

    def test_antithetic_reduces_variance(self):
        _, se_plain = mc_price(**BASE, n_paths=100_000, seed=2, antithetic=False)
        _, se_anti = mc_price(**BASE, n_paths=100_000, seed=2, antithetic=True)
        assert se_anti < se_plain
