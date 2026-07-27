"""Tests for: Random Pick with Weight

Run just this problem:      pytest -q            (from the problem folder)
Run every problem at once:  pytest -q            (from the problems/ root)
"""

import importlib.util
import random
from collections import Counter
from pathlib import Path

import pytest

# Load ../solution.py by path, under a name unique to this folder. This keeps
# every problem self-contained, so running pytest across all of them at once
# doesn't collide on the module name "solution".
_root = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "solution_" + _root.name.replace("-", "_"), _root / "solution.py"
)
_solution = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_solution)
Solution = _solution.Solution

# pickIndex() is randomized, so we can't assert exact return values like a
# normal problem. Instead we sample it many times per test case and check
# the empirical distribution against the expected probability of each index
# (weight / sum(weights)), within a tolerance.
#
# (id, w, num_trials, tolerance)
CASES = [
    pytest.param([1], 100, 0.0, id="example-1-single-weight"),
    pytest.param([1, 3], 20_000, 0.03, id="example-2-two-weights"),
    pytest.param([1, 1, 1, 1], 20_000, 0.03, id="uniform-weights"),
    pytest.param([1, 100], 20_000, 0.03, id="skewed-weights"),
]


@pytest.fixture(autouse=True)
def _seed():
    random.seed(42)


@pytest.mark.parametrize("w, num_trials, tolerance", CASES)
def test_random_pick_with_weight(w, num_trials, tolerance):
    solution = Solution(w)
    total = sum(w)
    expected_probs = [weight / total for weight in w]

    counts = Counter(solution.pickIndex() for _ in range(num_trials))

    for idx, expected_prob in enumerate(expected_probs):
        observed_prob = counts[idx] / num_trials
        assert observed_prob == pytest.approx(expected_prob, abs=tolerance), (
            f"index {idx}: expected ~{expected_prob:.3f}, got {observed_prob:.3f}"
        )


def test_pick_index_always_in_range():
    w = [3, 1, 2, 4]
    solution = Solution(w)
    for _ in range(1000):
        idx = solution.pickIndex()
        assert 0 <= idx < len(w)


def test_single_weight_always_returns_zero():
    solution = Solution([5])
    assert all(solution.pickIndex() == 0 for _ in range(50))