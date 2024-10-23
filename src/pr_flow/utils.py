from typing import List
from .state import Hunk
import re

def parse_patch(patch: str) -> List[Hunk]:
    """Parse the patch string and return a list of hunks."""
    hunks = []
    current_hunk = {"additions": [], "deletions": []}

    for line in patch.splitlines():
        if line.startswith("@@"):  # Hunk header
            if current_hunk["additions"] or current_hunk["deletions"]:
                hunks.append(current_hunk)
                current_hunk = {"additions": [], "deletions": []}
        elif line.startswith("+") and not line.startswith("+++"):  # Added line
            current_hunk["additions"].append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):  # Removed line
            current_hunk["deletions"].append(line[1:])

    if current_hunk["additions"] or current_hunk["deletions"]:
        hunks.append(current_hunk)

    return hunks

def parse_line_numbers(patch: str) -> str:
    """Parse the patch string and return a list of line numbers."""
    line_numbers = ""
    for hunk in patch.splitlines():
        if hunk.startswith("@@"):  # Hunk header
            match = re.search(r"\+(\d+)", hunk)
            if match:
                line_numbers = int(match.group(1))
                print(f"+{line_numbers}")
    return line_numbers
