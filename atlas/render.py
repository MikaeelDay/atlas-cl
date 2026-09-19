"""
Renders an architecture spec + its completion state into a single
Markdown file (ARCHITECTURE.md) that a human can read directly on
GitHub — a Mermaid flowchart of the sections and their dependencies,
plus a flat checklist marking what's done ("+") and what's next ("-").
"""

from __future__ import annotations

from atlas.spec import Spec, SpecNode
from atlas.state import State


def _topological_order(spec: Spec) -> list[SpecNode]:
    """
    Order nodes so every node comes after everything it depends on.
    Assumes spec.validate() has already ruled out cycles.
    """
    visited: set[str] = set()
    order: list[SpecNode] = []

    def visit(node: SpecNode) -> None:
        if node.id in visited:
            return
        visited.add(node.id)
        for dep_id in node.depends_on:
            dep = spec.get(dep_id)
            if dep is not None:
                visit(dep)
        order.append(node)

    for node in spec.nodes:
        visit(node)

    return order