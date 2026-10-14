from pydantic import BaseModel, ConfigDict, Field


class TripIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    owner_id: int
