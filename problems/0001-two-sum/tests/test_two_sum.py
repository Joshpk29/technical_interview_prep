"""Tests for: Two Sum

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

# (id, nums, target, expected)
# Cases below the divider are auto-filled from the examples on the problem
# page -- skim them once, the parser is best-effort.
CASES = [
    pytest.param([2, 7, 11, 15], 9, [0, 1], id="example-1"),
    pytest.param([3, 2, 4], 6, [1, 2], id="example-2"),
    pytest.param([3, 3], 6, [0, 1], id="example-3"),

]


@pytest.fixture
def solution():
    return Solution()


@pytest.mark.parametrize("nums, target, expected", CASES)
def test_two_sum(solution, nums, target, expected):
    result = solution.twoSum(nums, target)
    assert result == expected
