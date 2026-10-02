"""Skill taxonomy loaded from CSV. Replace data/skills.csv with ESCO/O*NET exports if desired."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple[str, ...]

    @property
    def surface_forms(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)


class Taxonomy:
    def __init__(self, skills: list[Skill]) -> None:
        self.skills = {s.name: s for s in skills}

    def __len__(self) -> int:
        return len(self.skills)

    def category(self, skill: str) -> str:
        return self.skills[skill].category

    @classmethod
    def from_csv(cls, path: str | Path = DATA_DIR / "skills.csv") -> Taxonomy:
        skills = []
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                aliases = tuple(a.strip() for a in row["aliases"].split("|") if a.strip())
                skills.append(Skill(row["skill"].strip().lower(), row["category"].strip(), aliases))
        return cls(skills)
