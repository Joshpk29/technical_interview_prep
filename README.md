# technical_interview_prep
# LeetCode practice
 
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
 
- **Solved** -- date you got it green (`2026-07-25`)
- **Min** -- minutes at the keyboard · **Try** -- submission attempts
- **Result** -- `solo` unaided · `hint` needed a hint · `peek` read a solution · `redo` revisited
- **Time / Space** -- the complexity you landed on (`O(n)` / `O(1)`)
- **Conf** -- 1 (would fail again) to 5 (could write it from memory)
- **Notes** -- the one insight you'd want on a re-read
| # | Problem | Diff | Solved |    Focus    |
|---|---------|------|--------|-------------|
| 1 | [FizzBuzz](0412-fizz-buzz/) | Easy | YES | Basic coding and operands |
| 2 | [Max Rectangle](0085-maximal-rectangle/) | Hard | YES | Dynamic programming, recursive functions |
