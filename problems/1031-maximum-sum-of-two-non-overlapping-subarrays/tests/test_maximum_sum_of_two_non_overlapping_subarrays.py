"""Tests for: Maximum Sum of Two Non-Overlapping Subarrays

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

# (id, nums, firstLen, secondLen, expected)
# Cases below the divider are auto-filled from the examples on the problem
# page -- skim them once, the parser is best-effort.
CASES = [
    pytest.param([0, 6, 5, 2, 2, 5, 1, 9, 4], 1, 2, 20, id="example-1"),
    pytest.param([3, 8, 1, 3, 2, 1, 8, 9, 0], 3, 2, 29, id="example-2"),
    pytest.param([2, 1, 5, 6, 0, 9, 5, 0, 3, 8], 4, 3, 31, id="example-3"),
]


@pytest.fixture
def solution():
    return Solution()


@pytest.mark.parametrize("nums, firstLen, secondLen, expected", CASES)
def test_maximum_sum_of_two_non_overlapping_subarrays(solution, nums, firstLen, secondLen, expected):
    result = solution.maxSumTwoNoOverlap(nums, firstLen, secondLen)
    assert result == expected
