"""
Evaluate Reverse Polish Notation (Medium)
https://leetcode.com/problems/evaluate-reverse-polish-notation

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        values = []
        for item in tokens:
            try:
                int(item)
                values.append(int(item))
            except:
                if item == '*':
                    item_0 = values.pop()
                    item_1 = values.pop()
                    values.append(item_1*item_0)
                if item == '+':
                    item_0 = values.pop()
                    item_1 = values.pop()
                    values.append(item_1+item_0)
                if item == '-':
                    item_0 = values.pop()
                    item_1 = values.pop()
                    values.append(item_1-item_0)
                if item == '/':
                    item_0 = values.pop()
                    item_1 = values.pop()
                    values.append(int(item_1/item_0))
        return values[0]
