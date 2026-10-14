import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth.models import User
from app.modules.auth.service import decode_token

# Brak nagłówka Authorization -> FastAPI samo zwraca 401, zanim wykona się endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_UNAUTHORIZED = HTTPException(
    status_code=401, detail="Invalid or missing token", headers={"WWW-Authenticate": "Bearer"}
)


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        data = decode_token(token)  # sprawdza podpis, algorytm i wygaśnięcie
        user_id = int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _UNAUTHORIZED
    user = db.get(User, user_id)
    if user is None:
        raise _UNAUTHORIZED
    return user
