#!/usr/bin/env python3
"""
Randomly pick a LeetCode question from questions.csv (weighted by Frequency),
then scaffold a practice folder:

    <out>/0001-two-sum/
        README.md              problem statement + metadata
        solution.py            real Python signature scraped from LeetCode
        tests/test_two_sum.py  pytest, parametrized, cases filled in from the
                               worked examples on the problem page

Usage:
    python pull_question.py                          # pick one, scaffold it
    python pull_question.py --csv questions.csv --out ./problems
    python pull_question.py --difficulty Medium --topic "Dynamic Programming"
    python pull_question.py --seed 42                # reproducible pick
    python pull_question.py --title "Two Sum"        # scaffold a specific one
    python pull_question.py --count 3                # scaffold several
    python pull_question.py --no-fetch               # offline, generic stub

CSV headers expected:
    Difficulty,Title,Frequency,Acceptance Rate,Link,Topics
"""

from __future__ import annotations

import argparse
import ast
import csv
import html
import json
import random
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

GRAPHQL_URL = "https://leetcode.com/graphql"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

QUESTION_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    exampleTestcases
    hints
    topicTags { name }
    codeSnippets { lang langSlug code }
  }
}
"""


# --------------------------------------------------------------------------- #
# CSV loading + weighted selection
# --------------------------------------------------------------------------- #

REQUIRED_COLUMNS = {"Difficulty", "Title", "Frequency", "Acceptance Rate", "Link", "Topics"}


def _to_float(value: str) -> float:
    """Parse '43.2', '43.2%', '1,234', '' -> float. Returns 0.0 on failure."""
    if value is None:
        return 0.0
    cleaned = str(value).strip().replace("%", "").replace(",", "").replace("$", "")
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def load_questions(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            sys.exit(f"{csv_path} appears to be empty.")
        missing = REQUIRED_COLUMNS - {f.strip() for f in reader.fieldnames}
        if missing:
            sys.exit(
                f"{csv_path} is missing expected column(s): {', '.join(sorted(missing))}\n"
                f"Found: {', '.join(reader.fieldnames)}"
            )
        rows = [{(k.strip() if k else k): (v or "").strip() for k, v in row.items()} for row in reader]

    questions = []
    for row in rows:
        if not row.get("Title") or not row.get("Link"):
            continue
        row["_frequency"] = _to_float(row.get("Frequency", ""))
        row["_acceptance"] = _to_float(row.get("Acceptance Rate", ""))
        questions.append(row)

    if not questions:
        sys.exit("No usable rows found in the CSV (need at least Title and Link).")
    return questions


def filter_questions(
    questions: Iterable[dict[str, Any]],
    difficulty: str | None = None,
    topic: str | None = None,
    min_frequency: float | None = None,
) -> list[dict[str, Any]]:
    result = list(questions)
    if difficulty:
        want = difficulty.strip().lower()
        result = [q for q in result if q.get("Difficulty", "").strip().lower() == want]
    if topic:
        want = topic.strip().lower()
        result = [q for q in result if want in q.get("Topics", "").lower()]
    if min_frequency is not None:
        result = [q for q in result if q["_frequency"] >= min_frequency]
    return result


def pick_weighted(
    questions: list[dict[str, Any]],
    rng: random.Random,
    k: int = 1,
) -> list[dict[str, Any]]:
    """Pick k distinct questions, probability proportional to Frequency.

    Rows with Frequency <= 0 still get a small floor weight so nothing is
    permanently unreachable. If every weight is 0 the pick is uniform.
    """
    if not questions:
        sys.exit("No questions matched your filters.")
    k = min(k, len(questions))

    freqs = [q["_frequency"] for q in questions]
    positive = [f for f in freqs if f > 0]
    floor = (min(positive) * 0.01) if positive else 1.0
    weights = [f if f > 0 else floor for f in freqs]

    # Sample without replacement, re-normalizing after each draw.
    pool = list(zip(questions, weights))
    chosen: list[dict[str, Any]] = []
    for _ in range(k):
        items, ws = zip(*pool)
        pick = rng.choices(range(len(items)), weights=ws, k=1)[0]
        chosen.append(items[pick])
        pool.pop(pick)
    return chosen


# --------------------------------------------------------------------------- #
# LeetCode fetch
# --------------------------------------------------------------------------- #


def slug_from_link(link: str) -> str:
    """https://leetcode.com/problems/two-sum/description/ -> two-sum"""
    match = re.search(r"/problems/([^/?#]+)", link)
    if match:
        return match.group(1)
    return re.sub(r"[^a-z0-9]+", "-", link.strip().lower()).strip("-") or "problem"


def fetch_question(slug: str, timeout: float = 15.0) -> dict[str, Any] | None:
    """Query the LeetCode GraphQL API. Returns None on any failure."""
    payload = json.dumps({"query": QUESTION_QUERY, "variables": {"titleSlug": slug}}).encode()
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Referer": f"https://leetcode.com/problems/{slug}/",
            "Origin": "https://leetcode.com",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"  ! could not fetch {slug} from LeetCode ({exc}); using generic stub", file=sys.stderr)
        return None
    question = (data.get("data") or {}).get("question")
    if not question:
        print(f"  ! LeetCode returned no data for '{slug}'; using generic stub", file=sys.stderr)
    return question


# --------------------------------------------------------------------------- #
# HTML -> Markdown (good enough for LeetCode's simple markup)
# --------------------------------------------------------------------------- #


def _plain_text(fragment: str) -> str:
    """Strip all tags and unescape -- used for <pre> blocks, which become code fences."""
    fragment = re.sub(r"<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(fragment).replace("\xa0", " ").strip("\n")


def pre_blocks(content: str) -> list[str]:
    """The <pre> example blocks of a problem statement, as plain text."""
    return [_plain_text(m) for m in re.findall(r"<pre[^>]*>(.*?)</pre>", content or "", flags=re.S)]


def html_to_markdown(raw: str) -> str:
    if not raw:
        return ""
    text = raw

    # <pre> becomes a fenced code block; pull it out first so inline markdown
    # (**bold**, `code`) never leaks inside the fence.
    blocks: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        blocks.append(_plain_text(match.group(1)))
        return f"\n\x00PRE{len(blocks) - 1}\x00\n"

    text = re.sub(r"<pre[^>]*>(.*?)</pre>", _stash, text, flags=re.S)

    text = re.sub(r"<sup>(.*?)</sup>", r"^\1", text, flags=re.S)
    text = re.sub(r"<sub>(.*?)</sub>", r"_\1", text, flags=re.S)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.S)
    text = re.sub(r"<(strong|b)[^>]*>(.*?)</\1>", r"**\2**", text, flags=re.S)
    text = re.sub(r"<(em|i)[^>]*>(.*?)</\1>", r"*\2*", text, flags=re.S)
    text = re.sub(r"\s*<li[^>]*>\s*", "\n- ", text)
    text = re.sub(r"\s*</li>", "", text)
    text = re.sub(r"</?(ul|ol)[^>]*>", "\n", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>", "\n\n", text)
    text = re.sub(r"<img[^>]*src=\"([^\"]+)\"[^>]*>", r"\n![image](\1)\n", text)
    text = re.sub(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"[\2](\1)", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)

    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)

    for index, block in enumerate(blocks):
        text = text.replace(f"\x00PRE{index}\x00", f"```\n{block}\n```")
    return text.strip()


# --------------------------------------------------------------------------- #
# Signature parsing
# --------------------------------------------------------------------------- #

GENERIC_SNIPPET = """class Solution:
    def solve(self, *args):
        \"\"\"TODO: replace with the real signature from the problem page.\"\"\"
"""


def python_snippet(question: dict[str, Any] | None) -> str:
    if not question:
        return GENERIC_SNIPPET
    snippets = question.get("codeSnippets") or []
    by_lang = {s.get("langSlug"): s.get("code", "") for s in snippets}
    return by_lang.get("python3") or by_lang.get("python") or GENERIC_SNIPPET


def _split_top_level(text: str, separator: str = ",") -> list[str]:
    """Split on `separator`, ignoring anything inside brackets or quotes."""
    parts, current, depth, quote = [], "", 0, None
    for index, char in enumerate(text):
        if quote:
            if char == quote and text[index - 1 : index] != "\\":
                quote = None
        elif char in "\"'":
            quote = char
        elif char in "[({":
            depth += 1
        elif char in "])}":
            depth -= 1
        elif char == separator and depth == 0:
            parts.append(current)
            current = ""
            continue
        current += char
    parts.append(current)
    return parts


def parse_entry_point(snippet: str) -> dict[str, Any]:
    """Describe the stub: class name, method, args, annotations, return type."""
    # Drop comment lines first -- LeetCode ships commented-out ListNode/TreeNode
    # definitions above the real class, and their __init__ must not be mistaken
    # for the entry point.
    code = "\n".join(line for line in snippet.splitlines() if not line.lstrip().startswith("#"))

    class_match = re.search(r"^class\s+(\w+)", code, flags=re.M)
    class_name = class_match.group(1) if class_match else "Solution"

    methods = re.findall(r"^\s+def\s+(\w+)", code, flags=re.M)
    signature = re.search(
        r"^\s+def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*([^\n:]+))?:", code, flags=re.S | re.M
    )
    if not signature:
        return {
            "class_name": class_name,
            "method": "solve",
            "args": ["args"],
            "annotations": {"args": ""},
            "returns": "",
            "methods": methods,
            "is_design": False,
        }

    args: list[str] = []
    annotations: dict[str, str] = {}
    for param in _split_top_level(signature.group(2)):
        param = param.split("=")[0].strip()
        if not param or param in ("self", "*", "/"):
            continue
        name, _, annotation = param.partition(":")
        name = name.strip().lstrip("*")
        if name:
            args.append(name)
            annotations[name] = annotation.strip()

    return {
        "class_name": class_name,
        "method": signature.group(1),
        "args": args or ["args"],
        "annotations": annotations,
        "returns": (signature.group(3) or "").strip(),
        "methods": methods,
        "is_design": class_name != "Solution" and "__init__" in methods,
    }


def uncomment_definitions(snippet: str) -> str:
    """LeetCode ships ListNode/TreeNode definitions commented out. Enable them.

    Prose lines ("# Definition for singly-linked list.") stay comments; the
    actual code lines ("# class ListNode:") get uncommented so the file runs.
    """
    if not re.search(r"^#\s*class\s+\w+", snippet, flags=re.M):
        return snippet

    out: list[str] = []
    inside = False
    for line in snippet.splitlines():
        if re.match(r"^#\s*class\s+\w+", line):
            inside = True
        elif inside:
            body = re.sub(r"^#\s?", "", line) if line.startswith("#") else line
            # The block ends at the first line that isn't indented comment code.
            if not line.startswith("#") or (body.strip() and not body.startswith(" ")):
                inside = False
                if line.strip():
                    out.append("")
                    out.append("")
        if inside and line.startswith("#"):
            out.append(re.sub(r"^#\s?", "", line))
        else:
            out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Example / test-case extraction
# --------------------------------------------------------------------------- #

_UNSET = object()


def parse_value(text: str) -> Any:
    """'[2,7,11,15]' -> [2, 7, 11, 15]; 'true' -> True. Raises on failure."""
    cleaned = text.strip().rstrip(",").strip()
    if not cleaned:
        raise ValueError("empty value")
    normalized = re.sub(r"\btrue\b", "True", cleaned)
    normalized = re.sub(r"\bfalse\b", "False", normalized)
    normalized = re.sub(r"\bnull\b", "None", normalized)
    return ast.literal_eval(normalized)


def parse_input_line(text: str, args: list[str]) -> list[Any] | None:
    """'nums = [2,7,11,15], target = 9' -> [[2, 7, 11, 15], 9]

    Falls back to positional order when the names don't match the signature.
    Returns None if the line can't be parsed into exactly len(args) values.
    """
    text = text.strip()
    if not text:
        return None

    # Locate `name =` at bracket depth 0.
    assignments: list[tuple[int, int, str]] = []
    depth, quote = 0, None
    for index, char in enumerate(text):
        if quote:
            if char == quote and text[index - 1 : index] != "\\":
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char in "[({":
            depth += 1
        elif char in "])}":
            depth -= 1
        elif char == "=" and depth == 0 and text[index + 1 : index + 2] != "=" and text[index - 1 : index] not in ("!", "<", ">", "="):
            end = index - 1
            while end >= 0 and text[end].isspace():
                end -= 1
            start = end
            while start >= 0 and (text[start].isalnum() or text[start] == "_"):
                start -= 1
            name = text[start + 1 : end + 1]
            if name and not name[0].isdigit():
                assignments.append((start + 1, index, name))

    values: dict[str, Any] = {}
    ordered: list[Any] = []
    try:
        if assignments:
            for position, (_, equals, name) in enumerate(assignments):
                stop = assignments[position + 1][0] if position + 1 < len(assignments) else len(text)
                raw = text[equals + 1 : stop].strip().rstrip(",")
                value = parse_value(raw)
                values[name] = value
                ordered.append(value)
        else:
            ordered = [parse_value(part) for part in _split_top_level(text)]
    except (ValueError, SyntaxError):
        return None

    if len(ordered) != len(args):
        return None
    if values and set(values) == set(args):
        return [values[name] for name in args]
    return ordered


def parse_examples(question: dict[str, Any] | None, args: list[str]) -> list[dict[str, Any]]:
    """Pull (inputs, expected) pairs out of the worked examples on the page.

    Inputs come from the `Input:` line of each <pre> block; when that can't be
    parsed we fall back to `exampleTestcases`, which is one raw value per line.
    Expected values only exist in the <pre> blocks.
    """
    if not question:
        return []

    fallback: list[list[Any]] = []
    raw_cases = (question.get("exampleTestcases") or "").strip()
    if raw_cases and args:
        lines = raw_cases.splitlines()
        if len(lines) % len(args) == 0:
            for start in range(0, len(lines), len(args)):
                try:
                    fallback.append([parse_value(line) for line in lines[start : start + len(args)]])
                except (ValueError, SyntaxError):
                    fallback.append([])

    examples: list[dict[str, Any]] = []
    for index, block in enumerate(pre_blocks(question.get("content") or "")):
        match = re.search(
            r"Input:?\s*(.*?)\n\s*Output:?\s*(.*?)(?:\n\s*(?:Explanation|Note):|\Z)",
            block,
            flags=re.S,
        )
        if not match:
            continue
        inputs = parse_input_line(match.group(1), args)
        if inputs is None and index < len(fallback) and fallback[index]:
            inputs = fallback[index]
        try:
            expected = parse_value(match.group(2).strip().splitlines()[0])
        except (ValueError, SyntaxError, IndexError):
            expected = _UNSET
        examples.append({"inputs": inputs, "expected": expected, "raw": block.strip()})

    return examples


def contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


# --------------------------------------------------------------------------- #
# Scaffolding
# --------------------------------------------------------------------------- #


def folder_name(row: dict[str, Any], question: dict[str, Any] | None, slug: str) -> str:
    number = (question or {}).get("questionFrontendId")
    if number and str(number).isdigit():
        return f"{int(number):04d}-{slug}"
    # Fall back to a leading number in the CSV title, e.g. "1. Two Sum"
    match = re.match(r"\s*(\d+)\s*[.\-]", row.get("Title", ""))
    if match:
        return f"{int(match.group(1)):04d}-{slug}"
    return slug


def test_filename(slug: str) -> str:
    """Unique basename per problem so pytest can collect every folder at once."""
    return "test_" + re.sub(r"[^0-9a-zA-Z]+", "_", slug).strip("_").lower() + ".py"


def build_readme(row: dict[str, Any], question: dict[str, Any] | None, slug: str) -> str:
    title = (question or {}).get("title") or row.get("Title", slug)
    number = (question or {}).get("questionFrontendId")
    heading = f"# {number}. {title}" if number else f"# {title}"

    difficulty = (question or {}).get("difficulty") or row.get("Difficulty", "?")
    topics = row.get("Topics", "")
    if question and question.get("topicTags"):
        topics = ", ".join(tag["name"] for tag in question["topicTags"])

    lines = [
        heading,
        "",
        f"**Link:** {row.get('Link', f'https://leetcode.com/problems/{slug}/')}",
        "",
        "| | |",
        "|---|---|",
        f"| Difficulty | {difficulty} |",
        f"| Frequency | {row.get('Frequency', 'n/a')} |",
        f"| Acceptance rate | {row.get('Acceptance Rate', 'n/a')} |",
        f"| Topics | {topics or 'n/a'} |",
        "",
        "---",
        "",
    ]

    body = html_to_markdown((question or {}).get("content") or "")
    if body:
        lines += ["## Problem", "", body, ""]
    else:
        lines += [
            "## Problem",
            "",
            "_Problem statement not fetched. Open the link above and paste it here._",
            "",
        ]

    hints = (question or {}).get("hints") or []
    if hints:
        lines += ["<details>", "<summary>Hints</summary>", ""]
        lines += [f"{i}. {html_to_markdown(h)}" for i, h in enumerate(hints, 1)]
        lines += ["", "</details>", ""]

    lines += [
        "---",
        "",
        "## Notes",
        "",
        "- **Approach:** ",
        "- **Time complexity:** ",
        "- **Space complexity:** ",
        "- **Gotchas:** ",
        "",
        "## Run the tests",
        "",
        "```bash",
        "pytest -q",
        "```",
        "",
    ]
    return "\n".join(lines)


def build_solution(row: dict[str, Any], question: dict[str, Any] | None, snippet: str) -> str:
    title = (question or {}).get("title") or row.get("Title", "")
    link = row.get("Link", "")
    difficulty = (question or {}).get("difficulty") or row.get("Difficulty", "")
    header = f'"""\n{title} ({difficulty})\n{link}\n\nApproach:\n    TODO\n\nTime:  O(?)\nSpace: O(?)\n"""\n\n'
    imports = "from typing import Any, Dict, List, Optional, Set, Tuple\n\n\n"

    body = uncomment_definitions(snippet)
    body = "\n".join(line.rstrip() for line in body.splitlines()).rstrip("\n")
    # If the entry-point method has no body, make it fail loudly instead of returning None.
    if not re.search(r"def\s+\w+\s*\([^)]*\)\s*(->[^\n:]*)?:\s*\n\s+\S", body):
        body += "\n        raise NotImplementedError"
    return header + imports + body + "\n"


NODE_HELPERS = '''

# --- helpers for linked-list / tree inputs (LeetCode passes these as lists) ---


def build_list(values):
    """[1, 2, 3] -> 1 -> 2 -> 3"""
    head = tail = None
    for value in values or []:
        node = _solution.ListNode(value)
        if head is None:
            head = tail = node
        else:
            tail.next = node
            tail = node
    return head


def to_list(node):
    """1 -> 2 -> 3 -> [1, 2, 3]"""
    values = []
    seen = set()
    while node is not None:
        if id(node) in seen:  # cycle guard so a bug can't hang the suite
            values.append("...cycle...")
            break
        seen.add(id(node))
        values.append(node.val)
        node = node.next
    return values


def build_tree(values):
    """LeetCode level-order (with nulls) -> TreeNode"""
    values = list(values or [])
    if not values or values[0] is None:
        return None
    root = _solution.TreeNode(values[0])
    queue, index = [root], 1
    while queue and index < len(values):
        node = queue.pop(0)
        if index < len(values):
            value = values[index]
            index += 1
            if value is not None:
                node.left = _solution.TreeNode(value)
                queue.append(node.left)
        if index < len(values):
            value = values[index]
            index += 1
            if value is not None:
                node.right = _solution.TreeNode(value)
                queue.append(node.right)
    return root


def to_level_order(root):
    """TreeNode -> LeetCode level-order list, trailing nulls trimmed"""
    if root is None:
        return []
    values, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            values.append(None)
            continue
        values.append(node.val)
        queue.extend([node.left, node.right])
    while values and values[-1] is None:
        values.pop()
    return values
'''


def build_tests(
    row: dict[str, Any],
    question: dict[str, Any] | None,
    entry: dict[str, Any],
    slug: str,
) -> tuple[str, int]:
    """Returns (file contents, number of auto-populated cases)."""
    title = (question or {}).get("title") or row.get("Title", "")
    args: list[str] = entry["args"]
    method: str = entry["method"]
    annotations: dict[str, str] = entry["annotations"]
    returns: str = entry["returns"]
    class_name: str = entry["class_name"]
    func_name = re.sub(r"[^0-9a-zA-Z]+", "_", slug).strip("_").lower() or "solution"

    header = [
        '"""Tests for: ' + title,
        "",
        "Run just this problem:      pytest -q            (from the problem folder)",
        "Run every problem at once:  pytest -q            (from the problems/ root)",
        '"""',
        "",
        "import importlib.util",
        "from pathlib import Path",
        "",
        "import pytest",
        "",
        "# Load ../solution.py by path, under a name unique to this folder. This keeps",
        "# every problem self-contained, so running pytest across all of them at once",
        '# doesn\'t collide on the module name "solution".',
        "_root = Path(__file__).resolve().parent.parent",
        "_spec = importlib.util.spec_from_file_location(",
        '    "solution_" + _root.name.replace("-", "_"), _root / "solution.py"',
        ")",
        "_solution = importlib.util.module_from_spec(_spec)",
        "_spec.loader.exec_module(_solution)",
        f"{class_name} = _solution.{class_name}",
        "",
    ]

    if entry["is_design"]:
        return "\n".join(header + _design_body(question, class_name, func_name)), _design_case_count(question)

    examples = parse_examples(question, args)
    populated = [ex for ex in examples if ex["inputs"] is not None and ex["expected"] is not _UNSET]

    # --- CASES table -------------------------------------------------------
    lines = [
        f"# (id, {', '.join(args)}, expected)",
        "# Cases below the divider are auto-filled from the examples on the problem",
        "# page -- skim them once, the parser is best-effort.",
        "CASES = [",
    ]
    for index, example in enumerate(examples, 1):
        if example["inputs"] is not None and example["expected"] is not _UNSET:
            values = ", ".join(repr(value) for value in example["inputs"])
            lines.append(f'    pytest.param({values}, {example["expected"]!r}, id="example-{index}"),')
        else:
            placeholder = ", ".join("None" for _ in args)
            reason = "couldn't auto-parse this example -- see the raw block at the bottom"
            lines.append(
                f'    pytest.param({placeholder}, None, id="example-{index}", '
                f'marks=pytest.mark.skip(reason="{reason}")),'
            )
    if not examples:
        placeholder = ", ".join("None" for _ in args)
        lines.append(f'    pytest.param({placeholder}, None, id="example-1"),')

    placeholder = ", ".join("None" for _ in args)
    for name in ("edge-empty", "edge-single", "edge-max-constraints"):
        lines.append(
            f'    pytest.param({placeholder}, None, id="{name}", '
            f'marks=pytest.mark.skip(reason="fill me in")),'
        )
    lines += ["]", ""]

    needs_nodes = any("ListNode" in a or "TreeNode" in a for a in list(annotations.values()) + [returns])
    if needs_nodes:
        lines.append(NODE_HELPERS.strip("\n"))
        lines.append("")

    # --- the test itself ---------------------------------------------------
    call_args = []
    for name in args:
        annotation = annotations.get(name, "")
        if "ListNode" in annotation:
            call_args.append(f"build_list({name})")
        elif "TreeNode" in annotation:
            call_args.append(f"build_tree({name})")
        else:
            call_args.append(name)
    call = f"{class_name.lower() if class_name != 'Solution' else 'solution'}.{method}({', '.join(call_args)})"

    if "ListNode" in returns:
        actual = "to_list(result)"
    elif "TreeNode" in returns:
        actual = "to_level_order(result)"
    else:
        actual = "result"

    approx = any(contains_float(ex["expected"]) for ex in populated)
    comparison = "pytest.approx(expected)" if approx else "expected"

    param_names = ", ".join(args + ["expected"])
    lines += [
        "",
        "@pytest.fixture",
        "def solution():",
        f"    return {class_name}()",
        "",
        "",
        f'@pytest.mark.parametrize("{param_names}", CASES)',
        f"def test_{func_name}(solution, {param_names}):",
    ]

    if returns == "None":
        # In-place problems: the expected value describes the mutated first argument.
        lines += [
            "    # This problem mutates its input in place; LeetCode's `Output:` line",
            f"    # describes `{args[0]}` after the call, not a return value.",
            f"    {call}",
            f"    assert {args[0]} == {comparison}",
        ]
    else:
        lines += [
            f"    result = {call}",
            f"    assert {actual} == {comparison}",
        ]

    if approx:
        lines += [
            "",
            "",
            "# Note: expected values are floats, so the assert uses pytest.approx().",
        ]

    unparsed = [ex for ex in examples if ex["inputs"] is None or ex["expected"] is _UNSET]
    if unparsed:
        lines += ["", "", "# Examples the parser couldn't turn into cases -- transcribe by hand:"]
        for example in unparsed:
            lines += ["#"] + ["# " + line for line in example["raw"].splitlines()]

    lines.append("")
    return "\n".join(header + lines), len(populated)


def _design_examples(question: dict[str, Any] | None) -> list[tuple[list[Any], list[Any], list[Any]]]:
    """Design problems: (operations, arguments, expected) triples."""
    cases = []
    for block in pre_blocks((question or {}).get("content") or ""):
        match = re.search(
            r"Input:?\s*(.*?)\n\s*Output:?\s*(.*?)(?:\n\s*(?:Explanation|Note):|\Z)",
            block,
            flags=re.S,
        )
        if not match:
            continue
        try:
            raw = match.group(1).strip().splitlines()
            operations = parse_value(raw[0])
            arguments = parse_value(raw[1]) if len(raw) > 1 else []
            expected = parse_value(match.group(2).strip().splitlines()[0])
        except (ValueError, SyntaxError, IndexError):
            continue
        if isinstance(operations, list) and isinstance(expected, list):
            cases.append((operations, arguments, expected))
    return cases


def _design_case_count(question: dict[str, Any] | None) -> int:
    return len(_design_examples(question))


def _design_body(question: dict[str, Any] | None, class_name: str, func_name: str) -> list[str]:
    cases = _design_examples(question)
    lines = [
        "# Design problem: each case is a sequence of operations run against one",
        "# instance. Auto-filled from the examples on the problem page.",
        "# (operations, arguments, expected)",
        "CASES = [",
    ]
    if cases:
        for index, (operations, arguments, expected) in enumerate(cases, 1):
            lines.append(f'    pytest.param({operations!r}, {arguments!r}, {expected!r}, id="example-{index}"),')
    else:
        lines.append('    pytest.param([], [], [], id="example-1", marks=pytest.mark.skip(reason="fill me in")),')
    lines += [
        '    pytest.param([], [], [], id="edge-cases", marks=pytest.mark.skip(reason="fill me in")),',
        "]",
        "",
        "",
        '@pytest.mark.parametrize("operations, arguments, expected", CASES)',
        f"def test_{func_name}(operations, arguments, expected):",
        "    instance = None",
        "    results = []",
        "    for operation, call_args in zip(operations, arguments):",
        f"        if operation == \"{class_name}\":",
        f"            instance = {class_name}(*call_args)",
        "            results.append(None)",
        "        else:",
        "            results.append(getattr(instance, operation)(*call_args))",
        "    assert results == expected",
        "",
    ]
    return lines


def scaffold(row: dict[str, Any], out_dir: Path, fetch: bool, force: bool) -> tuple[Path, bool, int]:
    """Returns (folder, created, auto_populated_case_count)."""
    slug = slug_from_link(row.get("Link", ""))
    question = fetch_question(slug) if fetch else None

    folder = out_dir / folder_name(row, question, slug)
    if folder.exists() and not force:
        return folder, False, 0

    (folder / "tests").mkdir(parents=True, exist_ok=True)

    snippet = python_snippet(question)
    entry = parse_entry_point(snippet)
    tests, case_count = build_tests(row, question, entry, slug)

    files = {
        folder / "README.md": build_readme(row, question, slug),
        folder / "solution.py": build_solution(row, question, snippet),
        folder / "tests" / test_filename(slug): tests,
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")

    return folder, True, case_count


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pick a LeetCode question weighted by frequency and scaffold a practice folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--csv", type=Path, default=Path("questions.csv"), help="Path to questions.csv")
    parser.add_argument("--out", type=Path, default=Path("problems"), help="Where to create problem folders")
    parser.add_argument("--count", type=int, default=1, help="How many questions to pick")
    parser.add_argument("--difficulty", help="Filter: Easy / Medium / Hard")
    parser.add_argument("--topic", help="Filter: substring match against the Topics column")
    parser.add_argument("--min-frequency", type=float, help="Filter: only rows at or above this frequency")
    parser.add_argument("--title", help="Skip the random pick and scaffold this exact title")
    parser.add_argument("--seed", type=int, help="Seed the RNG for a reproducible pick")
    parser.add_argument("--no-fetch", action="store_true", help="Skip LeetCode; emit a generic stub")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing problem folder")
    parser.add_argument("--dry-run", action="store_true", help="Show the pick without writing files")
    args = parser.parse_args(argv)

    questions = load_questions(args.csv)

    if args.title:
        want = args.title.strip().lower()
        picks = [q for q in questions if q["Title"].strip().lower() == want]
        if not picks:
            picks = [q for q in questions if want in q["Title"].lower()][:1]
        if not picks:
            sys.exit(f"No question matching title {args.title!r}")
    else:
        pool = filter_questions(questions, args.difficulty, args.topic, args.min_frequency)
        rng = random.Random(args.seed)
        picks = pick_weighted(pool, rng, args.count)
        print(f"Pool: {len(pool)} of {len(questions)} questions after filters.")

    for row in picks:
        print(
            f"\n-> {row['Title']}  [{row.get('Difficulty', '?')}] "
            f"freq={row.get('Frequency', '?')}  acc={row.get('Acceptance Rate', '?')}"
        )
        print(f"   {row.get('Link', '')}")
        if args.dry_run:
            continue
        folder, created, cases = scaffold(row, args.out, fetch=not args.no_fetch, force=args.force)
        if created:
            print(f"   created {folder}/  ({cases} test case{'' if cases == 1 else 's'} auto-filled)")
        else:
            print(f"   exists  {folder}/  (use --force to overwrite)")
        print(f"   run:    cd {folder} && pytest -q")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())