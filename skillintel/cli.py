"""Command-line demo: segment a synthetic workforce and print the result.

Usage: python -m skillintel.cli [--employees 60] [--k 5]
"""

from __future__ import annotations

import argparse

from .extraction import SkillExtractor
from .segmentation import segment_workforce
from .synthetic import generate_profiles
from .taxonomy import Taxonomy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--employees", type=int, default=60)
    parser.add_argument("--k", type=int, default=None)
    args = parser.parse_args()

    taxonomy = Taxonomy.from_csv()
    extractor = SkillExtractor(taxonomy)
    profiles = {ref: extractor.skill_set(t) for ref, t in generate_profiles(args.employees).items()}
    for seg in segment_workforce(profiles, taxonomy, k=args.k):
        print(f"Segment {seg.segment_id}: {seg.label}  (n={seg.size})")
        print(f"   top skills: {', '.join(seg.top_skills)}")


if __name__ == "__main__":
    main()
