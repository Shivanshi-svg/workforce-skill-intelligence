"""Rule-based skill extraction: alias matching with token-aware boundaries."""

from __future__ import annotations

import re
from collections import Counter

from .taxonomy import Taxonomy


class SkillExtractor:
    def __init__(self, taxonomy: Taxonomy) -> None:
        self.taxonomy = taxonomy
        self._patterns: dict[str, re.Pattern[str]] = {}
        for skill in taxonomy.skills.values():
            forms = sorted({f.lower() for f in skill.surface_forms}, key=len, reverse=True)
            alternation = "|".join(re.escape(f) for f in forms)
            # Word boundaries that also respect symbols used in skill names (c#, ci/cd, node.js).
            self._patterns[skill.name] = re.compile(
                rf"(?<![\w+#])(?:{alternation})(?![\w+#])"
            )

    def extract(self, text: str) -> Counter[str]:
        """Return canonical skills found in ``text`` with the number of mentions."""
        lowered = text.lower()
        found: Counter[str] = Counter()
        for name, pattern in self._patterns.items():
            count = len(pattern.findall(lowered))
            if count:
                found[name] = count
        return found

    def skill_set(self, text: str) -> set[str]:
        return set(self.extract(text))
