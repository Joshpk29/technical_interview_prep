"""Tests for: Letter Combinations of a Phone Number

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

# (id, digits, expected)
# Cases below the divider are auto-filled from the examples on the problem
# page -- skim them once, the parser is best-effort.
CASES = [
    pytest.param('23', ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf'], id="example-1"),
    pytest.param('2', ['a', 'b', 'c'], id="example-2"),
    pytest.param('234', ['adg', 'adh', 'adi', 'aeg', 'aeh', 'aei', 'afg', 'afh', 'afi','bdg', 'bdh', 'bdi', 'beg', 'beh', 'bei', 'bfg', 'bfh', 'bfi', 'cdg', 'cdh', 'cdi', 'ceg', 'ceh', 'cei', 'cfg', 'cfh', 'cfi'], id="example-3"),
]


@pytest.fixture
def solution():
    return Solution()


@pytest.mark.parametrize("digits, expected", CASES)
def test_letter_combinations_of_a_phone_number(solution, digits, expected):
    result = solution.letterCombinations(digits)
    assert result == expected
