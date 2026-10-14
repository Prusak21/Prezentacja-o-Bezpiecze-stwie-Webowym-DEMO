from pydantic import BaseModel, ConfigDict, Field


class EntryIn(BaseModel):
    note: str = Field(min_length=1, max_length=2000)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    trip_id: int
    note: str  # surowy tekst w JSON; ucieczka znaków to zadanie frontendu przy renderze
    lat: float | None
    lon: float | None
