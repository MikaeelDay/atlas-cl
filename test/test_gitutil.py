import subprocess
from pathlib import Path

import pytest

from atlas.gitutil import (
    GitError,
    changed_files_in_working_tree,
    changed_files_since_commit,
    current_commit,
    is_git_repo,
)

def _run(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

def _init_repo(path: Path) -> None:
    _run(["init"], cwd=path)
    _run(["config", "user.email", "test@example.com"], cwd=path)
    _run(["config", "user.name", "Test User"], cwd=path)