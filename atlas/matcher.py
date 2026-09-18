"""
Maps changed file paths to the architecture section(s) they belong to.

Each SpecNode carries a list of glob-style patterns in `paths`
(e.g. "auth/**", "users/models.py"). Given a list of files that
changed (typically from git), this module tells you which sections
were touched — so the CLI can say "looks like you worked on
'User Authentication'" instead of the user having to remember which
section owns which file.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch

from atlas.spec import Spec, SpecNode


@dataclass
class MatchResult:
    changed_file: str
    matched_nodes: list[SpecNode]

    @property
    def is_unmatched(self) -> bool:
        return not self.matched_nodes


def _normalize(path: str) -> str:
    """Use forward slashes and strip a leading './' so patterns behave
    the same regardless of OS or how the path was reported."""
    return path.replace("\\", "/").removeprefix("./")


def path_matches_pattern(path: str, pattern: str) -> bool:
    """
    True if `path` matches `pattern`.

    Supports the two glob shapes people actually write in a spec:
      - "auth/**"        -> anything under the auth/ directory (any depth)
      - "users/models.py" -> an exact file
      - "*.py"           -> a plain fnmatch glob
    """
    path = _normalize(path)
    pattern = _normalize(pattern)

    if pattern.endswith("/**"):
        prefix = pattern[: -len("/**")]
        return path == prefix or path.startswith(prefix + "/")

    return fnmatch(path, pattern)


def match_file(spec: Spec, changed_file: str) -> MatchResult:
    matched = [
        node
        for node in spec.nodes
        if any(path_matches_pattern(changed_file, p) for p in node.paths)
    ]
    return MatchResult(changed_file=changed_file, matched_nodes=matched)


def match_files(spec: Spec, changed_files: list[str]) -> list[MatchResult]:
    return [match_file(spec, f) for f in changed_files]


def sections_touched(spec: Spec, changed_files: list[str]) -> dict[str, list[str]]:
    """
    Convenience view: section id -> list of changed files that matched it.
    """
    touched: dict[str, list[str]] = {}
    for result in match_files(spec, changed_files):
        for node in result.matched_nodes:
            touched.setdefault(node.id, []).append(result.changed_file)
    return touched