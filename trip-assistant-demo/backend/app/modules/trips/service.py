from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.modules.auth.models import User
from app.modules.trips.models import Trip


def _deny() -> HTTPException:
    # 404 ukrywa, że cudzy zasób w ogóle istnieje; 403 to jawna odmowa.
    code = settings.IDOR_STATUS
    return HTTPException(code, "Not Found" if code == 404 else "Forbidden")


def get_owned_trip(db: Session, trip_id: int, user: User) -> Trip:
    """Bezpieczna ścieżka: wyprawa musi istnieć i należeć do zalogowanego użytkownika."""
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(404, "Not Found")
    if trip.owner_id != user.id:  # <- kontrola właściciela (obrona przed IDOR)
        raise _deny()
    return trip


def get_trip_unsafe(db: Session, trip_id: int) -> Trip:
    """WERSJA PODATNA (tylko do pokazu): brak sprawdzenia właściciela."""
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(404, "Not Found")
    return trip


def resolve_trip(db: Session, trip_id: int, user: User) -> Trip:
    if settings.DEMO_VULNERABLE_IDOR:
        return get_trip_unsafe(db, trip_id)
    return get_owned_trip(db, trip_id, user)
