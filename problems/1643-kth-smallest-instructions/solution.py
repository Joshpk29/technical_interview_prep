"""
Kth Smallest Instructions (Hard)
https://leetcode.com/problems/kth-smallest-instructions

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class Solution:
    all_solutions = []
    def search(self, destination: List[int], row: int, column:int, current_path: List[str]):
        if column < destination[1]:
            current_path = self.search(destination, row, column+1, current_path+'H')
        if row < destination[0]:
            current_path = self.search(destination, row+1, column, current_path+'V')
        if row == destination[0] and column==destination[1]:
            self.all_solutions.append(current_path)

        return current_path[:len(current_path)-1]

    def kthSmallestPath(self, destination: List[int], k: int) -> str:
        _ = self.search(destination, 0, 0, "")
        return self.all_solutions[k-1]
        
