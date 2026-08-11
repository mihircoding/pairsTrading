"""Shared synthetic fixtures, plus the loader that lets pytest import from the notebook.

Real market data is noisy and non-reproducible, so the tests use synthetic
series where the right answer is known by construction. This is also how you
should debug your own quant code: if it can't recover parameters you planted,
it can't be trusted on real data.
"""

import json
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# --------------------------------------------------------------------------
# Notebook loader
#
# All the project's functions live in src/pairs.ipynb, but the test files say
# `from src.pairs import ...`. A .ipynb file is JSON, not a Python module, so
# Python cannot import it directly.
#
# This reads the notebook, runs its code cells into one namespace, and registers
# that namespace under the module names the tests expect. Cells marked with
# `# skip-on-import` are skipped, so importing never downloads data or draws
# charts -- only the function definitions are executed.
# --------------------------------------------------------------------------

NOTEBOOK = Path(__file__).resolve().parent.parent / "src" / "pairs.ipynb"
SKIP_MARKER = "# skip-on-import"


def _run_notebook(path: Path) -> dict:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace: dict = {"__name__": "pairs_notebook"}

    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if SKIP_MARKER in source:
            continue
        exec(compile(source, str(path), "exec"), namespace)

    return namespace


def _register_as_modules(namespace: dict, names: tuple[str, ...]) -> None:
    package = types.ModuleType("src")
    package.__path__ = []  # marks it as a package so `src.pairs` resolves
    sys.modules["src"] = package

    for name in names:
        module = types.ModuleType(f"src.{name}")
        module.__dict__.update(namespace)
        sys.modules[f"src.{name}"] = module
        setattr(package, name, module)


if not NOTEBOOK.exists():
    raise FileNotFoundError(f"cannot find the notebook at {NOTEBOOK}")

_register_as_modules(_run_notebook(NOTEBOOK), ("pairs", "signals", "backtest", "data"))


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

N = 1500
SEED = 42


@pytest.fixture
def rng():
    return np.random.default_rng(SEED)


@pytest.fixture
def cointegrated_pair(rng):
    """A pair that is cointegrated by construction.

    x is a random walk; y = 10 + 2.5 * x + stationary AR(1) noise.
    The spread y - 2.5x is mean-reverting, so Engle-Granger should flag it.
    """
    idx = pd.bdate_range("2018-01-01", periods=N)
    x = pd.Series(100 + np.cumsum(rng.normal(0, 1, N)), index=idx, name="x")

    noise = np.zeros(N)
    for t in range(1, N):  # AR(1), phi=0.85 -> stationary
        noise[t] = 0.85 * noise[t - 1] + rng.normal(0, 1)
    y = pd.Series(10 + 2.5 * x.values + noise, index=idx, name="y")
    return y, x


@pytest.fixture
def independent_walks(rng):
    """Two unrelated random walks. NOT cointegrated."""
    idx = pd.bdate_range("2018-01-01", periods=N)
    a = pd.Series(100 + np.cumsum(rng.normal(0, 1, N)), index=idx, name="a")
    b = pd.Series(100 + np.cumsum(rng.normal(0, 1, N)), index=idx, name="b")
    return a, b
