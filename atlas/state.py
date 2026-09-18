"""
Persistence for completion state.

Why separate from the spec? Because the spec describes *intent*
(what the architecture should look like) while state describes
*progress* (what's actually been done). Keeping them apart means a
user can freely edit or regenerate the spec — rename a section,
add a new one, change dependencies — without ever losing track of
what they'd already marked complete for the sections that survive.

State lives in `.atlas/state.yaml`, next to a `.atlas/spec.yaml` at
the project root, mirroring how `.git/` sits at the root of a repo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

ATLAS_DIR = ".atlas"
STATE_FILENAME = "state.yaml"
SPEC_FILENAME = "spec.yaml"


@dataclass
class State:
    completed: dict[str, str] = field(default_factory=dict)
    """Maps section id -> ISO timestamp of when it was marked complete."""

    def is_done(self, node_id: str) -> bool:
        return node_id in self.completed

    def completed_ids(self) -> set[str]:
        return set(self.completed.keys())

    def mark_done(self, node_id: str) -> None:
        self.completed[node_id] = datetime.now(timezone.utc).isoformat()

    def mark_undone(self, node_id: str) -> None:
        self.completed.pop(node_id, None)


def atlas_dir(project_root: Path) -> Path:
    return project_root / ATLAS_DIR


def spec_path(project_root: Path) -> Path:
    return atlas_dir(project_root) / SPEC_FILENAME


def state_path(project_root: Path) -> Path:
    return atlas_dir(project_root) / STATE_FILENAME


def load_state(project_root: Path) -> State:
    path = state_path(project_root)
    if not path.exists():
        return State()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    completed = raw.get("completed", {}) or {}
    return State(completed=completed)


def save_state(state: State, project_root: Path) -> None:
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"completed": state.completed}
    path.write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def is_initialized(project_root: Path) -> bool:
    return spec_path(project_root).exists()