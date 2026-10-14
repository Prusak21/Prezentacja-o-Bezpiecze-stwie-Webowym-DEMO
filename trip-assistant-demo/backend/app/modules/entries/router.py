from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.dependencies import current_user
from app.modules.auth.models import User
from app.modules.entries.models import Entry
from app.modules.entries.schemas import EntryIn, EntryOut
from app.modules.trips.service import resolve_trip

router = APIRouter(prefix="/trips/{trip_id}/entries", tags=["entries"])


@router.get("", response_model=list[EntryOut])
def list_entries(trip_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    trip = resolve_trip(db, trip_id, user)
    return db.scalars(select(Entry).where(Entry.trip_id == trip.id).order_by(Entry.id)).all()


@router.post("", response_model=EntryOut, status_code=201)
def add_entry(trip_id: int, body: EntryIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    trip = resolve_trip(db, trip_id, user)
    entry = Entry(trip_id=trip.id, **body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
