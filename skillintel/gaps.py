"""Role-fit and skill-gap analysis against target role profiles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .taxonomy import DATA_DIR

Roles = dict[str, list[str]]


def load_roles(path: str | Path = DATA_DIR / "roles.json") -> Roles:
    return json.loads(Path(path).read_text(encoding="utf-8"))


@dataclass(frozen=True)
class GapReport:
    role: str
    coverage: float
    matched: list[str]
    missing: list[str]


def analyse_gap(skills: set[str], role: str, roles: Roles) -> GapReport:
    if role not in roles:
        raise KeyError(role)
    required = roles[role]
    matched = [s for s in required if s in skills]
    missing = [s for s in required if s not in skills]
    return GapReport(role, round(len(matched) / len(required), 3), matched, missing)


def best_fit_roles(skills: set[str], roles: Roles, top_n: int = 3) -> list[GapReport]:
    reports = [analyse_gap(skills, role, roles) for role in roles]
    return sorted(reports, key=lambda r: (-r.coverage, r.role))[:top_n]


def segment_gap(
    member_skills: list[set[str]], role: str, roles: Roles
) -> dict[str, float]:
    """Share of segment members lacking each skill the role requires (0 = none, 1 = all)."""
    required = roles[role]
    if not member_skills:
        return {s: 1.0 for s in required}
    return {
        s: round(sum(s not in m for m in member_skills) / len(member_skills), 3) for s in required
    }
