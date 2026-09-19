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