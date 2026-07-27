# Technical Interview Prep 
Each folder is one problem, scaffolded by `pull_question.py`: the statement, a
solution stub with the real signature, and pytest cases pre-filled from the
worked examples on the problem page.
 
## Pick a new problem
 
```bash
python pull_question.py                            # weighted by Frequency
python pull_question.py --difficulty Medium
python pull_question.py --topic "Dynamic Programming"
python pull_question.py --count 3                  # scaffold a batch
python pull_question.py --title "Two Sum"          # a specific one
python pull_question.py --seed 42                  # reproducible pick
```
 
## Run the tests
 
```bash
pip install pytest                  # once
 
cd 0001-two-sum && pytest -q        # just this problem
```
 
A fresh folder fails with `NotImplementedError` on the example cases -- that's
the correct starting point. The three skipped rows (`edge-empty`, `edge-single`,
`edge-max-constraints`) are yours: delete the `marks=pytest.mark.skip(...)`
argument to turn one on.
 
## Loop
 
1. Read the problem's `README.md`.
2. Write `solution.py` until the example cases pass.
3. Add your own edge cases, then re-run.
4. Log a row in the table below.
## Progress


| # | Problem | Diff | Solved |    Focus    | Completion Date | 
|---|---------|------|--------|-------------|-----------------|
| 1 | [FizzBuzz](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0412-fizz-buzz) | Easy | YES | Basic coding and operands | 07/25/2026
| 2 | [Max Rectangle](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0085-maximal-rectangle/) | Hard | YES | Dynamic programming, recursive functions |  07/25/2026
| 3 | [Sort GCD](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/1998-gcd-sort-of-an-array) | Hard | NO |  |
| 4 | [Maximum Sum](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/1031-maximum-sum-of-two-non-overlapping-subarrays) | Medium | YES | Optimal Selection, Sliding Windows |  07/26/2026
| 5 | [$k^{th}$ Smallest Instruction](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/1643-kth-smallest-instructions) | Hard | YES | Optimal pathing, recursive programming |  07/26/2026
| 6 | [Two Sum](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0001-two-sum) | Easy | YES | basic iteration, programming |  07/26/2026
| 7 | [Phone Combinations](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0017-letter-combinations-of-a-phone-number) | Medium | YES | Combinatronics |  07/26/2026
| 8 | [New 21 Game](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0837-new-21-game) | Medium | YES | Probability & Statistics |  07/27/2026
| 9 | [Reverse Polish Notation](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0150-evaluate-reverse-polish-notation) | Medium | YES | Stack, Mathimatics |  07/27/2026
| 10 | [Sales by Day of the Week](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0150-evaluate-reverse-polish-notation) | Hard | NO | Databases |  07/27/2026
| 11 | [Random Pick With Weight](https://github.com/Joshpk29/technical_interview_prep/tree/main/problems/0528-random-pick-with-weight) | Medium | YES | Statistics & Probability |  07/27/2026
