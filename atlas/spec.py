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
    path: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)

@dataclass
class Spec:
    project_name: str
    nodes: list[SpecNode] = field(default_factory=list)

    def get(self,node_id: str) -> SpecNode:
        return next((n for n in self.nodes if n.id == node_id),None)
