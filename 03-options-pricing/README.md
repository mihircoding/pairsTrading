# Project 3 — Options Pricing Lab

Implement the three standard ways to price an option — the Black-Scholes closed form,
binomial trees, and Monte Carlo — plus the Greeks and an implied-volatility solver. Then
put it on the internet: this project includes a Streamlit app (`app.py`) that turns your
implementations into an interactive pricing tool you can deploy for free and link on your
resume.

The three methods deliberately overlap: they price the *same* option, so they must agree.
That agreement is your test oracle — the binomial tree must converge to Black-Scholes, and
Monte Carlo must land within its own confidence interval of it. Pricing models that can
cross-check each other is exactly how real derivatives desks validate their libraries.

## The model

Black-Scholes assumes the stock follows geometric Brownian motion:

```
dS = r*S*dt + sigma*S*dW        (risk-neutral dynamics)
```

Under those assumptions a European call has a closed-form price:

```
d1 = (ln(S/K) + (r + sigma^2/2)*T) / (sigma*sqrt(T))
d2 = d1 - sigma*sqrt(T)

call = S*N(d1) - K*exp(-r*T)*N(d2)
put  = K*exp(-r*T)*N(-d2) - S*N(-d1)
```

where N is the standard normal CDF (`scipy.stats.norm.cdf`). You don't need to *derive*
this to implement it, but you should understand the pieces: `N(d2)` is the risk-neutral
probability the option finishes in the money; `S*N(d1)` is the expected value of receiving
the stock, given exercise; discounting at `exp(-r*T)` brings the strike payment to today.

**Put-call parity** — `call - put = S - K*exp(-r*T)` — holds regardless of any model
assumptions (it's pure no-arbitrage). It is the first thing the tests check and the first
thing an interviewer asks.

## The Greeks

Sensitivities of the price to each input. Traders think entirely in these:

| Greek | Derivative | Meaning |
|-------|-----------|---------|
| Delta | dV/dS | shares of stock that hedge the option |
| Gamma | d²V/dS² | how fast delta changes; cost of rehedging |
| Vega  | dV/dsigma | exposure to volatility changes |
| Theta | dV/dT (decay) | value lost per day, all else equal |
| Rho   | dV/dr | rate sensitivity |

You implement them twice: analytically (closed forms, in the docstrings) and by **finite
differences** (bump the input, reprice, take the slope). The test that checks your analytic
delta against your own finite-difference delta is checking internal consistency — a
technique that transfers to every model you'll ever build.

## Implied volatility

The market quotes option *prices*; everyone converts them to *implied vols* — the sigma
that makes Black-Scholes reproduce the market price. There's no closed form, so you invert
numerically. Bisection is slow and bulletproof; Newton's method is fast (vega is the
derivative you need) but can misbehave for deep in/out-of-the-money options. Implement
bisection first; Newton is a stretch goal.

## Repo layout

```
03-options-pricing/
├── README.md
├── requirements.txt
├── app.py                   # Streamlit web app (complete — deploy it when tests pass)
├── src/
│   ├── black_scholes.py     # TODO: closed-form price + analytic Greeks
│   ├── binomial.py          # TODO: Cox-Ross-Rubinstein tree, European + American
│   ├── monte_carlo.py       # TODO: GBM simulation pricer with standard error
│   └── implied_vol.py       # TODO: bisection solver
└── tests/
    ├── test_black_scholes.py
    ├── test_binomial.py
    ├── test_monte_carlo.py
    └── test_implied_vol.py
```

## Build it: milestones

**Milestone 1 — Black-Scholes price** (`src/black_scholes.py :: bs_price`)
The formula above. Tests check a hand-verifiable case (S=100, K=100, T=1, r=5%, sigma=20%
→ call ≈ 10.4506) and put-call parity across a grid of inputs.

**Milestone 2 — Analytic Greeks** (`src/black_scholes.py :: bs_greeks`)
Formulas in the docstring. Tests check signs, bounds (0 < call delta < 1), and agreement
with finite differences of your own Milestone 1.

**Milestone 3 — Binomial tree** (`src/binomial.py :: crr_price`)
Cox-Ross-Rubinstein: build the terminal payoffs, discount backwards. With
`american=True`, compare continuation value to immediate exercise at every node — this
prices American options, which Black-Scholes cannot. Tests: European tree converges to
Black-Scholes as steps grow; American put ≥ European put.

**Milestone 4 — Monte Carlo** (`src/monte_carlo.py :: mc_price`)
Simulate terminal prices with the exact GBM formula, average discounted payoffs, and
report the **standard error** — a Monte Carlo price without an error bar is meaningless.
The test checks your price lands within 3 standard errors of Black-Scholes.

**Milestone 5 — Implied vol** (`src/implied_vol.py :: implied_vol`)
Bisection on sigma in [1e-4, 5]. Test: price an option at sigma=0.2, invert the price,
recover 0.2 to four decimals.

**Milestone 6 — Ship it**
Run `streamlit run app.py` locally. The app detects which milestones you've implemented
and unlocks tabs as you go. When everything works, deploy it (next section).

## Deploying the app as a free live website

Your first instinct might be Vercel — but Vercel's free tier is built around JavaScript
and static sites; it can't host a long-running Python process like Streamlit. For Python
apps the free options that actually fit:

1. **Streamlit Community Cloud** (recommended) — free, deploys straight from a public
   GitHub repo, zero config:
   - Push this repo to GitHub.
   - Go to https://share.streamlit.io and sign in with GitHub.
   - "Create app" → pick the repo, branch `main`, main file `03-options-pricing/app.py`.
   - It builds from `requirements.txt` in the same folder and gives you a public
     `*.streamlit.app` URL. Put that URL at the top of this README and on your resume.
2. **Hugging Face Spaces** — also free; create a Space with the Streamlit SDK and push
   the folder there. Nice if you want everything under one profile with other ML work.
3. **Render** — free web-service tier runs `streamlit run app.py`; sleeps after
   inactivity, cold-starts in ~30s.

Free tiers sleep when idle — the first visitor after a quiet spell waits ~30 seconds.
That's fine for a resume demo.

## Pitfalls checklist

- **Units**: T is in YEARS (30 days ≈ 0.0822), sigma and r are annualized decimals
  (20% = 0.2). Mixing daily and annual units is the classic bug.
- **T → 0 and sigma → 0** edge cases: the formulas divide by `sigma*sqrt(T)`. Handle
  expiry (return intrinsic value) before the formula.
- **Theta sign conventions** differ by textbook (per-year vs per-day, sign flipped).
  Pick one, document it, test it.
- **Monte Carlo without a seed** makes tests flaky; without a standard error it's
  not a price, it's a random number.

## Stretch goals

- Newton-Raphson implied vol using your analytic vega; compare iteration counts
  against bisection.
- Antithetic variates in the Monte Carlo — measure the variance reduction.
- Full volatility smile: pull a real option chain (yfinance `Ticker.option_chain`),
  run your implied-vol solver across strikes, and plot the smile in the app.
- Price an Asian option (path-dependent) by extending the Monte Carlo to simulate
  full paths — now you know why Monte Carlo exists.

## Resources

- John Hull, *Options, Futures, and Other Derivatives* — chapters 13, 15, 19-21 cover
  everything here. THE reference; older editions are fine and cheap.
- Sheldon Natenberg, *Option Volatility and Pricing* — how traders actually think about
  Greeks and vol. Less math, more intuition.
- Steven Shreve, *Stochastic Calculus for Finance II* — if you want the real derivation
  of Black-Scholes. Graduate-level; optional.
- Espen Haug, *The Complete Guide to Option Pricing Formulas* — a cookbook of closed
  forms, useful for adding more models to the app.
- QuantLib (https://www.quantlib.org) and its Python bindings — the open-source
  industry-grade pricing library. Validate your numbers against it as a stretch goal.
- Streamlit docs: https://docs.streamlit.io — the whole framework is learnable in an hour.
