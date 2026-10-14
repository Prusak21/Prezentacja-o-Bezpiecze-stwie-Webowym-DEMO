from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import Base, engine
from app.core.settings import settings
from app.modules.auth.router import router as auth_router
from app.modules.entries.router import router as entries_router
from app.modules.trips.router import router as trips_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Trip Assistant: demo bezpieczeństwa", lifespan=lifespan)

# CORS: jawna lista originów z konfiguracji (nigdy "*" razem z credentials).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(trips_router)
app.include_router(entries_router)


@app.get("/health")
def health():
    return {"status": "ok", "vulnerable_idor_demo": settings.DEMO_VULNERABLE_IDOR}
