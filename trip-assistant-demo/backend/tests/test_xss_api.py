"""Pokaz 3 (strona API): backend zwraca dane jako JSON, escaping robi frontend."""
PAYLOAD = "<img src=x onerror=alert(1)>"


def test_api_returns_note_as_json_not_html(client, bob):
    trip_id = client.post("/trips", json={"title": "T"}, headers=bob).json()["id"]
    r = client.post(f"/trips/{trip_id}/entries", json={"note": PAYLOAD}, headers=bob)
    assert r.status_code == 201
    assert r.headers["content-type"].startswith("application/json")
    assert r.json()["note"] == PAYLOAD  # dane surowe; bezpieczne wyświetlenie: frontend/src/main.js
