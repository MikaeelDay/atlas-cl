"""
Thin wrapper around the `git` command-line tool.

Runs git as a subprocess and parses its output, rather than pulling in
a heavier third-party library like GitPython. Two things atlas needs
from git:
  1. What's changed in the working tree right now (uncommitted work).
  2. What's changed between two commits (for "what happened since I
     last checked" tracking).
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(Exception):
    """Raised when a git command fails or the project isn't a git repo."""

def _run_git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as e:
        raise GitError("git is not installed or not on PATH") from e
    except subprocess.CalledProcessError as e:
        raise GitError(f"git {' '.join(args)} failed: {e.stderr.strip()}") from e
    return result.stdout

def is_git_repo(project_root: Path) -> bool:
    try:
        _run_git(["rev-parse", "--is-inside-work-tree"], cwd=project_root)
        return True
    except GitError:
        return False