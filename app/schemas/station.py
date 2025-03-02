from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.station import StationStatus
import uuid


class StationBase(BaseModel):
    name: str
    location: str
    max_capacity_kw: float


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    max_capacity_kw: Optional[float] = None
    status: Optional[StationStatus] = None


class StationStatusUpdate(BaseModel):
    status: StationStatus


class StationScheduledStatusChange(BaseModel):
    status: StationStatus
    delay_seconds: int


class StationInDBBase(StationBase):
    id: uuid.UUID
    status: StationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Station(StationInDBBase):
    pass
