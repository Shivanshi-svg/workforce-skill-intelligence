import pytest

from skillintel.gaps import analyse_gap, best_fit_roles, load_roles, segment_gap

ROLES = load_roles()


def test_gap_report():
    r = analyse_gap({"python", "sql", "git"}, "data_engineer", ROLES)
    assert r.coverage == round(3 / 7, 3)
    assert "azure" in r.missing and "python" in r.matched


def test_best_fit_orders_by_coverage():
    best = best_fit_roles({"sql", "excel", "power bi", "statistics", "communication"}, ROLES)
    assert best[0].role == "data_analyst" and best[0].coverage == 1.0


def test_unknown_role_raises():
    with pytest.raises(KeyError):
        analyse_gap(set(), "wizard", ROLES)


def test_segment_gap_shares():
    gaps = segment_gap([{"sql"}, {"sql", "excel"}], "data_analyst", ROLES)
    assert gaps["sql"] == 0.0 and gaps["excel"] == 0.5 and gaps["power bi"] == 1.0
