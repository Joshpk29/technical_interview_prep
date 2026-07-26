"""
Maximal Rectangle (Hard)
https://leetcode.com/problems/maximal-rectangle

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple




class Solution:
    def search_area(self, row, col, matrix):
        sum = 1
        if row == len(matrix)-1 and  col == len(matrix[row]) - 1: #corner
            return sum
        if row == len(matrix)-1: # bottom
            if int(matrix[row][col+1]) == 1:
                sum += self.search_area((row), (col+1), matrix)
            else:
                return sum
        if col == len(matrix[row]) - 1: #right most
            if int(matrix[row+1][col]) == 1:
                sum += self.search_area((row+1), (col), matrix)
            else:
                return sum
        if row < len(matrix) - 1 and col < len(matrix[row]) - 1: #full diagonal move
            if int(matrix[row+1][col+1]) == 1 and int(matrix[row+1][col]) == 1 and int(matrix[row][col+1]) == 1:
                sum += self.search_area((row+1), (col+1), matrix) + self.search_area((row+1), (col), matrix) + self.search_area((row), (col+1), matrix) - 1 #-1, for double searching
        return sum

    
    def maximalRectangle(self, matrix: List[List[str]]) -> int:
        max_area = 0
        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                if int(matrix[row][col]) == 0:
                    continue
                else:
                    area = self.search_area(row, col, matrix)
                    if area > max_area:
                        max_area = area
        return max_area