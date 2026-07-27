"""
New 21 Game (Medium)
https://leetcode.com/problems/new-21-game

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

import random

from typing import Any, Dict, List, Optional, Set, Tuple


class Solution:
    def new21Game(self, n: int, k: int, maxPts: int) -> float:
        # Edge cases
        if k == 0 or n >= k - 1 + maxPts:
            return 1.0

        dp = [0.0] * (k - 1 + maxPts + 1)
        dp[0] = 1.0
        window_sum = 1.0  # sum of dp[j] for j in [i-maxPts, i-1]
        result = 0.0

        for i in range(1, k - 1 + maxPts + 1):
            dp[i] = window_sum / maxPts

            if i < k:
                window_sum += dp[i]
            elif i<=n:
                result += dp[i]

            if i - maxPts >= 0:
                window_sum -= dp[i - maxPts]

        return result


