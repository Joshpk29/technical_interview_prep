"""
Two Sum (Easy)
https://leetcode.com/problems/two-sum

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        for index_0 in range(len(nums)):
            for index_1 in range(len(nums)):
                if index_0 != index_1 and nums[index_0] + nums[index_1] == target:
                    return [index_0, index_1]
