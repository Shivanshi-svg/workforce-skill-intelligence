import pytest

from skillintel.extraction import SkillExtractor
from skillintel.segmentation import segment_workforce
from skillintel.synthetic import generate_profiles
from skillintel.taxonomy import Taxonomy

TAXONOMY = Taxonomy.from_csv()


def _profiles(n=60):
    extractor = SkillExtractor(TAXONOMY)
    return {r: extractor.skill_set(t) for r, t in generate_profiles(n).items()}


def test_every_employee_lands_in_exactly_one_segment():
    profiles = _profiles()
    segments = segment_workforce(profiles, TAXONOMY, k=5)
    members = [m for s in segments for m in s.members]
    assert sorted(members) == sorted(profiles)


def test_segmentation_is_deterministic():
    a = segment_workforce(_profiles(), TAXONOMY, k=5, seed=1)
    b = segment_workforce(_profiles(), TAXONOMY, k=5, seed=1)
    assert [(s.label, s.size) for s in a] == [(s.label, s.size) for s in b]


def test_expected_archetypes_are_recovered():
    labels = " ".join(s.label for s in segment_workforce(_profiles(), TAXONOMY, k=5))
    for expected in ("power bi", "people management", "react", "data engineering"):
        assert expected in labels


def test_too_few_employees_raises():
    with pytest.raises(ValueError):
        segment_workforce({"a": {"python"}}, TAXONOMY)
