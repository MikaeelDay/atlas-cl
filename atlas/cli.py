"""
Command-line interface for atlas.

Wires spec, state, matcher, gitutil, and render together into four
commands: init, status, complete, diff. This is intentionally the
last layer built — everything it calls was already tested on its own.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from atlas.gitutil import GitError, changed_files_in_working_tree, is_git_repo
from atlas.matcher import sections_touched
from atlas.render import render_markdown
from atlas.spec import SpecError, load_spec, save_spec
from atlas.state import atlas_dir, is_initialized, load_state, save_state, spec_path

app = typer.Typer(help="A living architecture map for your project.")
console = Console()

ARCHITECTURE_FILENAME = "ARCHITECTURE.md"


def _project_root() -> Path:
    return Path.cwd()


def _require_initialized() -> Path:
    root = _project_root()
    if not is_initialized(root):
        console.print(
            "[red]atlas hasn't been set up here yet.[/red] Run [bold]atlas init <spec.yaml>[/bold] first."
        )
        raise typer.Exit(code=1)
    return root


def _regenerate_architecture_md(root: Path) -> None:
    spec = load_spec(spec_path(root))
    state = load_state(root)
    content = render_markdown(spec, state)
    (root / ARCHITECTURE_FILENAME).write_text(content, encoding="utf-8")