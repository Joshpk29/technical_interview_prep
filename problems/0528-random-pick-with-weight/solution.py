"""
Random Pick with Weight (Medium)
https://leetcode.com/problems/random-pick-with-weight

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import random

class Solution:

    def __init__(self, w: List[int]):
        self.w = w
        self.weighted_list = []
        for item in range(len(self.w)):
            for i in range(self.w[item]):
                self.weighted_list.append(item)

    def pickIndex(self) -> int:
        return random.choice(self.weighted_list)
