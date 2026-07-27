"""Tests for: New 21 Game

Run just this problem:      pytest -q            (from the problem folder)
Run every problem at once:  pytest -q            (from the problems/ root)
"""

import importlib.util
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

# (id, n, k, maxPts, expected)
# Cases below the divider are auto-filled from the examples on the problem
# page -- skim them once, the parser is best-effort.
CASES = [
    pytest.param(10, 1, 10, 1.0, id="example-1"),
    pytest.param(6, 1, 10, 0.6, id="example-2"),
    pytest.param(21, 17, 10, 0.7327777870686082, id="example-3"),
]


@pytest.fixture
def solution():
    return Solution()


@pytest.mark.parametrize("n, k, maxPts, expected", CASES)
def test_new_21_game(solution, n, k, maxPts, expected):
    result = solution.new21Game(n, k, maxPts)
    assert result == expected


# Note: expected values are floats, so the assert uses pytest.approx().
