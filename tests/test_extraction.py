from skillintel.extraction import SkillExtractor
from skillintel.taxonomy import Taxonomy

EXTRACTOR = SkillExtractor(Taxonomy.from_csv())


def test_aliases_map_to_canonical_skills():
    skills = EXTRACTOR.skill_set("Used PySpark on Databricks, plus scikit-learn and MLflow.")
    assert {"apache spark", "machine learning", "mlops"} <= skills


def test_symbol_heavy_names_match():
    skills = EXTRACTOR.skill_set("Built C# services with CI/CD pipelines and Node.js tooling.")
    assert {"c#", "ci/cd", "javascript"} <= skills


def test_no_substring_false_positives():
    # "java" must not match inside "javascript"; "ts" must not match inside "results".
    skills = EXTRACTOR.skill_set("Strong results with javascript only.")
    assert "java" not in skills and "typescript" not in skills and "javascript" in skills


def test_hypothesis_testing_is_not_software_testing():
    assert "software testing" not in EXTRACTOR.skill_set("Hypothesis testing and reporting")
    assert "statistics" in EXTRACTOR.skill_set("Hypothesis testing and reporting")


def test_counts_mentions():
    assert EXTRACTOR.extract("python, Python and python3")["python"] == 3
