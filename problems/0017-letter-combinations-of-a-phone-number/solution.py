"""
Letter Combinations of a Phone Number (Medium)
https://leetcode.com/problems/letter-combinations-of-a-phone-number

Approach:
    TODO

Time:  O(?)
Space: O(?)
"""

from typing import Any, Dict, List, Optional, Set, Tuple

def get_combinations(array):
    if not array:
        return []
    
    # Helper to clean out any rogue bracket formatting
    def clean(val):
        return str(val).replace("[", "").replace("]", "").strip()
    
    # Initialize with the first row
    result = [clean(item) for item in array[0]]
    
    # Process remaining rows
    for row in array[1:]:
        temp = []
        for current_str in result:
            for item in row:
                temp.append(current_str + clean(item))
        result = temp  
        
    return result

class Solution:
    number_dict = {
        "2": ["a", "b", "c"],
        "3": ["d", "e", "f"],
        "4": ["g", "h", "i"],
        "5": ["j", "k", "l"],
        "6": ["m", "n", "o"],
        "7": ["p", "q", "r", "s"],
        "8": ["t", "u", "v"],
        "9": ["x", "y", "z", "z"]
    }
    def letterCombinations(self, digits: str) -> List[str]:
        possible = []
        for number in digits:
            possible.append(self.number_dict.get(number))
        return get_combinations(possible)

