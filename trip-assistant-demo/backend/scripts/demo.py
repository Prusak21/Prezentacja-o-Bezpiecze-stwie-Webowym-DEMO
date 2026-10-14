"""Skrypt do pokazu na żywo. Uruchom serwer (uvicorn), potem:  python scripts/demo.py
Opcjonalnie inny adres:  python scripts/demo.py http://localhost:8000
"""
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
OK_ORIGIN = "http://localhost:5173"
EVIL_ORIGIN = "https://evil.example"


def show(title: str, resp: httpx.Response, note: str = "") -> None:
    print(f"  {title:<48} -> {resp.status_code} {note}")


def login(email: str) -> dict:
    httpx.post(f"{BASE}/auth/register", json={"email": email, "password": "pass12345"})
    r = httpx.post(f"{BASE}/auth/login", data={"username": email, "password": "pass12345"})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


print(f"Serwer: {BASE}  ({httpx.get(BASE + '/health').json()})\n")

print("1) CORS (preflight)")
for origin in (OK_ORIGIN, EVIL_ORIGIN):
    r = httpx.options(f"{BASE}/trips", headers={"Origin": origin, "Access-Control-Request-Method": "GET"})
    show(f"OPTIONS /trips, Origin {origin}", r, f"allow-origin: {r.headers.get('access-control-allow-origin')}")

print("\n2) Middleware autoryzacji")
show("GET /trips bez tokenu", httpx.get(f"{BASE}/trips"))
show("GET /trips ze sfałszowanym tokenem", httpx.get(f"{BASE}/trips", headers={"Authorization": "Bearer abc.def.ghi"}))

print("\n3) IDOR: alice kontra wyprawa Boba")
alice, bob = login("alice@example.com"), login("bob@example.com")
trip_id = httpx.post(f"{BASE}/trips", json={"title": "Dolomity"}, headers=bob).json()["id"]
print(f"  Bob utworzył wyprawę ID {trip_id}")
show(f"PATCH /trips/{trip_id} jako alice", httpx.patch(f"{BASE}/trips/{trip_id}", json={"title": "HACKED"}, headers=alice))
show(f"DELETE /trips/{trip_id} jako alice", httpx.delete(f"{BASE}/trips/{trip_id}", headers=alice))
show("DELETE /trips/999999 jako alice (nieistniejące)", httpx.delete(f"{BASE}/trips/999999", headers=alice))
after = httpx.get(f"{BASE}/trips/{trip_id}", headers=bob)
show(f"GET /trips/{trip_id} jako bob (sprawdzenie)", after, after.json().get("title", ""))
