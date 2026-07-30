import pytest

from src.black_scholes import bs_price
from src.implied_vol import implied_vol


class TestImpliedVol:
    @pytest.mark.parametrize("sigma", [0.08, 0.2, 0.55, 1.2])
    def test_round_trip(self, sigma):
        price = bs_price(100.0, 100.0, 0.5, 0.03, sigma, "call")
        assert implied_vol(price, 100.0, 100.0, 0.5, 0.03, "call") == pytest.approx(
            sigma, abs=1e-4
        )

    def test_round_trip_puts_and_moneyness(self):
        for K in (80.0, 100.0, 125.0):
            price = bs_price(100.0, K, 1.0, 0.05, 0.3, "put")
            iv = implied_vol(price, 100.0, K, 1.0, 0.05, "put")
            assert iv == pytest.approx(0.3, abs=1e-4)

    def test_unbracketable_price_raises(self):
        # A call can never be worth more than the stock
        with pytest.raises(ValueError):
            implied_vol(150.0, 100.0, 100.0, 1.0, 0.05, "call")
