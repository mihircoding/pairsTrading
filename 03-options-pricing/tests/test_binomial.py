import pytest

from src.binomial import crr_price
from src.black_scholes import bs_price

BASE = dict(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)


class TestEuropean:
    @pytest.mark.parametrize("kind", ["call", "put"])
    def test_converges_to_black_scholes(self, kind):
        tree = crr_price(**BASE, kind=kind, steps=500)
        closed = bs_price(**BASE, kind=kind)
        assert tree == pytest.approx(closed, abs=0.05)

    def test_error_shrinks_with_steps(self):
        closed = bs_price(**BASE, kind="call")
        err_small = abs(crr_price(**BASE, kind="call", steps=50) - closed)
        err_large = abs(crr_price(**BASE, kind="call", steps=800) - closed)
        assert err_large < err_small


class TestAmerican:
    def test_american_put_worth_more(self):
        # ITM put: early exercise has real value
        params = dict(S=90.0, K=110.0, T=1.0, r=0.05, sigma=0.2)
        euro = crr_price(**params, kind="put", steps=500, american=False)
        amer = crr_price(**params, kind="put", steps=500, american=True)
        assert amer > euro + 1e-4

    def test_american_call_no_dividends_equals_european(self):
        # Classic result: never exercise a call on a non-dividend stock early
        euro = crr_price(**BASE, kind="call", steps=500, american=False)
        amer = crr_price(**BASE, kind="call", steps=500, american=True)
        assert amer == pytest.approx(euro, abs=1e-6)

    def test_american_never_below_intrinsic(self):
        amer = crr_price(S=80.0, K=110.0, T=0.5, r=0.05, sigma=0.2,
                         kind="put", steps=300, american=True)
        assert amer >= 30.0 - 1e-9
