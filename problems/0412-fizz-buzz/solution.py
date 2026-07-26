"""
Fizz Buzz (Easy)
https://leetcode.com/problems/fizz-buzz

Time:  O(n)
Space: O(n)
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        rtn_arr = []
        for value in range(1,(n+1)):
            if value % 3 == 0 and value % 5 == 0:
                rtn_arr.append("FizzBuzz")
            elif value % 3 == 0:
               rtn_arr.append("Fizz")
            elif value % 5 == 0:
                rtn_arr.append("Buzz")
            else:
                rtn_arr.append(str(value))
        return rtn_arr