from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.dependencies import current_user
from app.modules.auth.models import User
from app.modules.trips.models import Trip
from app.modules.trips.schemas import TripIn, TripOut
from app.modules.trips.service import resolve_trip

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripOut])
def list_trips(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Trip).where(Trip.owner_id == user.id)).all()


@router.post("", response_model=TripOut, status_code=201)
def create_trip(body: TripIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    trip = Trip(title=body.title, owner_id=user.id)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return resolve_trip(db, trip_id, user)


@router.patch("/{trip_id}", response_model=TripOut)
def update_trip(trip_id: int, body: TripIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    trip = resolve_trip(db, trip_id, user)
    trip.title = body.title
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=204)
def delete_trip(trip_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    trip = resolve_trip(db, trip_id, user)
    db.delete(trip)
    db.commit()
