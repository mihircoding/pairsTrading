import numpy as np
import pytest

from src.black_scholes import bs_greeks, bs_price, fd_greek

# The canonical hand-checkable case: S=K=100, T=1y, r=5%, sigma=20%
BASE = dict(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)


class TestPrice:
    def test_known_call_value(self):
        assert bs_price(**BASE, kind="call") == pytest.approx(10.4506, abs=1e-3)

    def test_known_put_value(self):
        assert bs_price(**BASE, kind="put") == pytest.approx(5.5735, abs=1e-3)

    def test_put_call_parity_grid(self):
        """call - put = S - K*exp(-rT), model-free, must hold everywhere."""
        for S in (80.0, 100.0, 120.0):
            for T in (0.1, 0.5, 2.0):
                for sigma in (0.1, 0.4):
                    c = bs_price(S, 100.0, T, 0.03, sigma, "call")
                    p = bs_price(S, 100.0, T, 0.03, sigma, "put")
                    assert c - p == pytest.approx(S - 100.0 * np.exp(-0.03 * T), abs=1e-9)

    def test_expiry_returns_intrinsic(self):
        assert bs_price(110.0, 100.0, 0.0, 0.05, 0.2, "call") == pytest.approx(10.0)
        assert bs_price(110.0, 100.0, 0.0, 0.05, 0.2, "put") == pytest.approx(0.0)

    def test_deep_itm_call_approaches_forward(self):
        # S >> K: call ~ S - K*exp(-rT)
        c = bs_price(500.0, 100.0, 1.0, 0.05, 0.2, "call")
        assert c == pytest.approx(500.0 - 100.0 * np.exp(-0.05), abs=1e-2)


class TestGreeks:
    def test_call_delta_bounds_and_atm(self):
        g = bs_greeks(**BASE, kind="call")
        assert 0.0 < g["delta"] < 1.0
        assert g["delta"] == pytest.approx(0.6368, abs=1e-3)  # N(d1), d1=0.35

    def test_put_call_delta_relation(self):
        gc = bs_greeks(**BASE, kind="call")
        gp = bs_greeks(**BASE, kind="put")
        assert gc["delta"] - gp["delta"] == pytest.approx(1.0, abs=1e-9)

    def test_gamma_and_vega_positive_and_shared(self):
        gc = bs_greeks(**BASE, kind="call")
        gp = bs_greeks(**BASE, kind="put")
        assert gc["gamma"] > 0 and gc["vega"] > 0
        assert gc["gamma"] == pytest.approx(gp["gamma"])
        assert gc["vega"] == pytest.approx(gp["vega"])

    @pytest.mark.parametrize("greek", ["delta", "gamma", "vega", "theta", "rho"])
    def test_analytic_matches_finite_difference(self, greek):
        """Your two implementations must agree with each other."""
        analytic = bs_greeks(**BASE, kind="call")[greek]
        numeric = fd_greek(bs_price, greek, **BASE, kind="call")
        assert analytic == pytest.approx(numeric, rel=1e-3, abs=1e-4)
