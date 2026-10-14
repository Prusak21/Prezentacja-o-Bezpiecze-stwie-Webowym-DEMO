"""Pokaz 2: IDOR. Alice próbuje edytować i usuwać wyprawę Boba po ID."""
from app.core.settings import settings


def bobs_trip(client, bob) -> int:
    return client.post("/trips", json={"title": "Dolomity"}, headers=bob).json()["id"]


def test_alice_cannot_delete_bobs_trip(client, alice, bob):
    trip_id = bobs_trip(client, bob)
    r = client.delete(f"/trips/{trip_id}", headers=alice)
    assert r.status_code == 404
    assert client.get(f"/trips/{trip_id}", headers=bob).status_code == 200  # wyprawa nadal istnieje


def test_alice_cannot_edit_bobs_trip(client, alice, bob):
    trip_id = bobs_trip(client, bob)
    r = client.patch(f"/trips/{trip_id}", json={"title": "HACKED"}, headers=alice)
    assert r.status_code == 404
    assert client.get(f"/trips/{trip_id}", headers=bob).json()["title"] == "Dolomity"


def test_alice_cannot_read_bobs_entries(client, alice, bob):
    trip_id = bobs_trip(client, bob)
    client.post(f"/trips/{trip_id}/entries", json={"note": "tajne"}, headers=bob)
    assert client.get(f"/trips/{trip_id}/entries", headers=alice).status_code == 404


def test_policy_403(client, alice, bob, monkeypatch):
    monkeypatch.setattr(settings, "IDOR_STATUS", 403)
    trip_id = bobs_trip(client, bob)
    assert client.delete(f"/trips/{trip_id}", headers=alice).status_code == 403


def test_foreign_and_missing_look_the_same_with_404(client, alice, bob):
    trip_id = bobs_trip(client, bob)
    foreign = client.delete(f"/trips/{trip_id}", headers=alice)
    missing = client.delete("/trips/99999", headers=alice)
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()  # nie da się rozróżnić, czy ID istnieje


def test_owner_can_delete_own_trip(client, bob):
    trip_id = bobs_trip(client, bob)
    assert client.delete(f"/trips/{trip_id}", headers=bob).status_code == 204


def test_vulnerable_mode_shows_the_bug(client, alice, bob, monkeypatch):
    """Po włączeniu DEMO_VULNERABLE_IDOR alice faktycznie usuwa cudzą wyprawę."""
    monkeypatch.setattr(settings, "DEMO_VULNERABLE_IDOR", True)
    trip_id = bobs_trip(client, bob)
    assert client.delete(f"/trips/{trip_id}", headers=alice).status_code == 204
    assert client.get(f"/trips/{trip_id}", headers=bob).status_code == 404  # wyprawa Boba zniknęła
