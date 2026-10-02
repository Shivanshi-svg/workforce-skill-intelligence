from fastapi.testclient import TestClient

from skillintel.api import create_app
from skillintel.store import ProfileStore
from skillintel.synthetic import generate_profiles


def _client():
    return TestClient(create_app(ProfileStore(), salt="test-salt"))


def _load(client, n=30):
    ids = {}
    for ref, text in generate_profiles(n).items():
        ids[ref] = client.post("/profiles", json={"employee_ref": ref, "text": text}).json()
    return ids


def test_profile_ingest_pseudonymises_and_extracts():
    r = _client().post("/profiles", json={"employee_ref": "HR-1", "text": "Python and Docker"})
    body = r.json()
    assert r.status_code == 201 and body["employee_id"].startswith("emp_")
    assert "HR-1" not in body["employee_id"] and body["skills"] == ["docker", "python"]


def test_fit_for_role_and_best_fit():
    c = _client()
    emp = c.post("/profiles", json={"employee_ref": "x", "text": "SQL, Excel, Power BI"}).json()
    eid = emp["employee_id"]
    fit = c.get(f"/employees/{eid}/fit", params={"role": "data_analyst"}).json()
    assert fit["coverage"] == 0.6 and fit["missing"] == ["statistics", "communication"]
    assert c.get(f"/employees/{eid}/fit").json()["best_fit"][0]["role"] == "data_analyst"
    assert c.get(f"/employees/{eid}/fit", params={"role": "nope"}).status_code == 404
    assert c.get("/employees/ghost/fit").status_code == 404


def test_segmentation_and_segment_gaps():
    c = _client()
    _load(c)
    seg = c.post("/segments", json={"k": 5}).json()["segments"]
    assert sum(s["size"] for s in seg) == 30
    gaps = c.get("/segments/gaps", params={"role": "ai_engineer", "k": 5}).json()
    assert gaps["role"] == "ai_engineer" and len(gaps["segments"]) == len(seg)


def test_segmentation_needs_enough_profiles():
    assert _client().post("/segments", json={}).status_code == 422
