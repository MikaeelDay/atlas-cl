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

def test_is_git_repo_false_outside_repo(tmp_path: Path):
    assert not is_git_repo(tmp_path)


def test_is_git_repo_true_inside_repo(tmp_path: Path):
    _init_repo(tmp_path)
    assert is_git_repo(tmp_path)

def test_current_commit_returns_a_hash(tmp_path: Path):
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hello")
    _run(["add", "a.txt"], cwd=tmp_path)
    _run(["commit", "-m", "first commit"], cwd=tmp_path)

    commit_hash = current_commit(tmp_path)
    assert len(commit_hash) == 40
    assert all(c in "0123456789abcdef" for c in commit_hash)


def test_current_commit_raises_when_no_commits_yet(tmp_path: Path):
    _init_repo(tmp_path)
    with pytest.raises(GitError):
        current_commit(tmp_path)

def test_changed_files_in_working_tree_detects_untracked_and_modified(
    tmp_path: Path,
):
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hello")
    _run(["add", "a.txt"], cwd=tmp_path)
    _run(["commit", "-m", "first commit"], cwd=tmp_path)

    (tmp_path / "a.txt").write_text("changed")
    (tmp_path / "b.txt").write_text("new file")

    changed = set(changed_files_in_working_tree(tmp_path))
    assert changed == {"a.txt", "b.txt"}


def test_changed_files_in_working_tree_empty_when_clean(tmp_path: Path):
    _init_repo(tmp_path)
    (tmp_path / "a.txt").write_text("hello")
    _run(["add", "a.txt"], cwd=tmp_path)
    _run(["commit", "-m", "first commit"], cwd=tmp_path)

    assert changed_files_in_working_tree(tmp_path) == []

