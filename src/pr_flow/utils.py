from typing import List
from .state import Hunk

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