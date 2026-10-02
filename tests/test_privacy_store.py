from skillintel.privacy import pseudonymise
from skillintel.store import ProfileStore


def test_pseudonym_is_stable_salted_and_hides_reference():
    a = pseudonymise("HR-1001", "salt-a")
    assert a == pseudonymise("HR-1001", "salt-a")
    assert a != pseudonymise("HR-1001", "salt-b")
    assert "1001" not in a


def test_store_roundtrip_and_delete():
    s = ProfileStore()
    s.upsert("e1", {"python", "sql"})
    s.upsert("e1", {"python"})
    assert s.get("e1") == {"python"}
    assert s.delete("e1") and s.get("e1") is None and not s.delete("e1")
