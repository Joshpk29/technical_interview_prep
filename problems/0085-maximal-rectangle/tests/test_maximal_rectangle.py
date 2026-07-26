"""Tests for: Maximal Rectangle

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

# (id, matrix, expected)
# Cases below the divider are auto-filled from the examples on the problem
# page -- skim them once, the parser is best-effort.
CASES = [
    pytest.param([['1', '0', '1', '0', '0'], ['1', '0', '1', '1', '1'], ['1', '1', '1', '1', '1'], ['1', '0', '0', '1', '0']], 6, id="example-1"),
    pytest.param([['0']], 0, id="example-2"),
    pytest.param([['1']], 1, id="example-3"),
    pytest.param(None, None, id="edge-empty", marks=pytest.mark.skip(reason="fill me in")),
    pytest.param(None, None, id="edge-single", marks=pytest.mark.skip(reason="fill me in")),
    pytest.param(None, None, id="edge-max-constraints", marks=pytest.mark.skip(reason="fill me in")),
]


@pytest.fixture
def solution():
    return Solution()


@pytest.mark.parametrize("matrix, expected", CASES)
def test_maximal_rectangle(solution, matrix, expected):
    result = solution.maximalRectangle(matrix)
    assert result == expected
