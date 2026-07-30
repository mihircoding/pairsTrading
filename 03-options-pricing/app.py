"""Interactive options pricing app (Streamlit).

This file is complete — it is the glue, not the lesson. It calls YOUR
implementations in src/, and unlocks each tab as you finish the milestone
behind it, so you can run it from day one:

    streamlit run app.py

Deployment (free): push the repo to GitHub, then on https://share.streamlit.io
create an app pointing at 03-options-pricing/app.py. See README.md.
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.binomial import crr_price
from src.black_scholes import bs_greeks, bs_price
from src.implied_vol import implied_vol
from src.monte_carlo import mc_price

st.set_page_config(page_title="Options Pricing Lab", page_icon=":chart:", layout="wide")
st.title("Options Pricing Lab")
st.caption(
    "Black-Scholes, binomial trees, and Monte Carlo — three models, one option, "
    "and they'd better agree. Source: github.com — projectTemplatesQuant, project 03."
)


def locked(milestone: str):
    st.info(f"Locked — implement **{milestone}** in `src/` and the tests for it, "
            "then reload this page.")


with st.sidebar:
    st.header("Contract")
    kind = st.radio("Type", ["call", "put"], horizontal=True)
    S = st.number_input("Spot S", value=100.0, min_value=0.01)
    K = st.number_input("Strike K", value=100.0, min_value=0.01)
    T = st.slider("Expiry T (years)", 0.02, 3.0, 1.0, 0.02)
    r = st.slider("Rate r", 0.0, 0.10, 0.05, 0.005)
    sigma = st.slider("Volatility sigma", 0.05, 1.0, 0.2, 0.01)

tab_bs, tab_tree, tab_mc, tab_iv = st.tabs(
    ["Black-Scholes & Greeks", "Binomial tree", "Monte Carlo", "Implied vol"]
)

with tab_bs:
    try:
        price = bs_price(S, K, T, r, sigma, kind)
        st.metric(f"{kind.capitalize()} price", f"{price:.4f}")
        try:
            g = bs_greeks(S, K, T, r, sigma, kind)
            cols = st.columns(5)
            for col, name in zip(cols, ["delta", "gamma", "vega", "theta", "rho"]):
                col.metric(name.capitalize(), f"{g[name]:.4f}")
        except NotImplementedError:
            locked("Milestone 2 (analytic Greeks)")

        # Price vs spot curve — the classic hockey stick smoothing out with time
        spots = np.linspace(0.5 * K, 1.5 * K, 120)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(spots, [bs_price(s, K, T, r, sigma, kind) for s in spots],
                label=f"T = {T:.2f}y")
        payoff = np.maximum(spots - K, 0) if kind == "call" else np.maximum(K - spots, 0)
        ax.plot(spots, payoff, "--", color="gray", label="payoff at expiry")
        ax.axvline(S, color="tab:red", lw=0.8)
        ax.set_xlabel("Spot"); ax.set_ylabel("Value"); ax.legend()
        st.pyplot(fig)
    except NotImplementedError:
        locked("Milestone 1 (bs_price)")

with tab_tree:
    try:
        steps = st.slider("Tree steps", 10, 1000, 200, 10)
        american = st.checkbox("American exercise")
        tree = crr_price(S, K, T, r, sigma, kind, steps=steps, american=american)
        st.metric("Tree price", f"{tree:.4f}")
        try:
            closed = bs_price(S, K, T, r, sigma, kind)
            st.metric("vs Black-Scholes (European)", f"{tree - closed:+.4f}")
            ns = np.unique(np.linspace(10, max(steps, 50), 25, dtype=int))
            fig, ax = plt.subplots(figsize=(8, 3.5))
            ax.plot(ns, [crr_price(S, K, T, r, sigma, kind, steps=int(n),
                                   american=american) for n in ns], marker="o", ms=3)
            ax.axhline(closed, color="gray", ls="--", label="Black-Scholes")
            ax.set_xlabel("Steps"); ax.set_ylabel("Price"); ax.legend()
            ax.set_title("Convergence of the tree to the closed form")
            st.pyplot(fig)
        except NotImplementedError:
            pass
    except NotImplementedError:
        locked("Milestone 3 (crr_price)")

with tab_mc:
    try:
        n_paths = st.select_slider("Paths", [10_000, 50_000, 100_000, 500_000],
                                   value=100_000)
        anti = st.checkbox("Antithetic variates")
        price, se = mc_price(S, K, T, r, sigma, kind, n_paths=n_paths,
                             seed=0, antithetic=anti)
        c1, c2 = st.columns(2)
        c1.metric("MC price", f"{price:.4f}")
        c2.metric("Std error", f"{se:.4f}")
        st.write(f"95% CI: [{price - 1.96 * se:.4f}, {price + 1.96 * se:.4f}]")
        try:
            st.write(f"Black-Scholes: {bs_price(S, K, T, r, sigma, kind):.4f} "
                     "— should sit inside that interval ~95% of the time.")
        except NotImplementedError:
            pass
    except NotImplementedError:
        locked("Milestone 4 (mc_price)")

with tab_iv:
    try:
        # default market price = model price at sigma, so round-trip is visible
        default = 10.45
        try:
            default = round(bs_price(S, K, T, r, sigma, kind), 2)
        except NotImplementedError:
            pass
        market = st.number_input("Market option price", value=default, min_value=0.01)
        try:
            iv = implied_vol(market, S, K, T, r, kind)
            st.metric("Implied volatility", f"{iv:.2%}")
        except ValueError as e:
            st.warning(f"No solution: {e}")
    except NotImplementedError:
        locked("Milestone 5 (implied_vol)")
