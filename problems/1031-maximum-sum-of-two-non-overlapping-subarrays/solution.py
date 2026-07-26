"""
Maximum Sum of Two Non-Overlapping Subarrays (Medium)
https://leetcode.com/problems/maximum-sum-of-two-non-overlapping-subarrays

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class Solution:
    def maxSumTwoNoOverlap(self, nums: List[int], firstLen: int, secondLen: int) -> int:
        first_len_sums = []
        second_len_sums = []
        for index in range(len(nums)):
            if index + firstLen <= len(nums):
                f_sum = sum(nums[index:(index+firstLen)])
                first_len_sums.append([f_sum, index, index+firstLen])

            if index + secondLen <= len(nums):
                s_sum = sum(nums[index:(index+secondLen)])
                second_len_sums.append([s_sum,index, index+secondLen])

        possible_sums = []
        for index_0 in range(len(first_len_sums)):
            for index_1 in range(len(second_len_sums)):
                if first_len_sums[index_0][2] < second_len_sums[index_1][1]:
                    possible_sums.append((first_len_sums[index_0][0]+second_len_sums[index_1][0]))
                elif first_len_sums[index_0][1] > second_len_sums[index_1][2]:
                    possible_sums.append((first_len_sums[index_0][0]+second_len_sums[index_1][0]))
        return max(possible_sums)