"""
Data model for an architecture spec.

A spec is a directed graph of sections (nodes). Each section describes
one piece of the intended architecture (e.g. "User Authentication"),
which file paths belong to it, and which other sections it depends on
(so we can figure out what the "next" section is).

The spec itself only describes the *intended* structure — completion
state lives separately in state.py, so editing the spec never wipes
out progress.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


class SpecError(Exception):
    """Raised when a spec file is missing, malformed, or inconsistent."""


@dataclass
class SpecNode:
    id: str
    name: str
    description: str = ""
    paths: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Spec:
    project_name: str
    nodes: list[SpecNode] = field(default_factory=list)

    def get(self, node_id: str) -> SpecNode | None:
        return next((n for n in self.nodes if n.id == node_id), None)

    def roots(self) -> list[SpecNode]:
        """Nodes with no dependencies — valid starting points."""
        return [n for n in self.nodes if not n.depends_on]

    def ready_nodes(self, completed_ids: set[str]) -> list[SpecNode]:
        """Nodes whose dependencies are all completed, but that aren't themselves done yet."""
        return [
            n
            for n in self.nodes
            if n.id not in completed_ids
            and all(dep in completed_ids for dep in n.depends_on)
        ]

    def validate(self) -> None:
        ids = [n.id for n in self.nodes]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise SpecError(f"Duplicate section ids: {sorted(dupes)}")
        id_set = set(ids)
        for n in self.nodes:
            unknown = [d for d in n.depends_on if d not in id_set]
            if unknown:
                raise SpecError(
                    f"Section '{n.id}' depends on unknown section(s): {unknown}"
                )
        _check_no_cycles(self.nodes)


def _check_no_cycles(nodes: list[SpecNode]) -> None:
    graph = {n.id: n.depends_on for n in nodes}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n_id: WHITE for n_id in graph}

    def visit(node_id: str, stack: list[str]) -> None:
        color[node_id] = GRAY
        for dep in graph[node_id]:
            if color[dep] == GRAY:
                cycle = " -> ".join(stack + [dep])
                raise SpecError(f"Circular dependency detected: {cycle}")
            if color[dep] == WHITE:
                visit(dep, stack + [dep])
        color[node_id] = BLACK

    for n_id in graph:
        if color[n_id] == WHITE:
            visit(n_id, [n_id])


def load_spec(path: Path | str) -> Spec:
    path = Path(path)
    if not path.exists():
        raise SpecError(f"Spec file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise SpecError(f"Could not parse YAML in {path}: {e}") from e

    project_name = raw.get("project_name", "")
    nodes_raw = raw.get("sections", [])
    if not isinstance(nodes_raw, list):
        raise SpecError("'sections' must be a list")

    nodes = []
    for i, n in enumerate(nodes_raw):
        if "id" not in n or "name" not in n:
            raise SpecError(f"Section #{i} is missing required field 'id' or 'name'")
        nodes.append(
            SpecNode(
                id=n["id"],
                name=n["name"],
                description=n.get("description", ""),
                paths=n.get("paths", []) or [],
                depends_on=n.get("depends_on", []) or [],
            )
        )

    spec = Spec(project_name=project_name, nodes=nodes)
    spec.validate()
    return spec


def save_spec(spec: Spec, path: Path) -> None:
    data = {
        "project_name": spec.project_name,
        "sections": [
            {
                "id": n.id,
                "name": n.name,
                "description": n.description,
                "paths": n.paths,
                "depends_on": n.depends_on,
            }
            for n in spec.nodes
        ],
    }
    path.write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )