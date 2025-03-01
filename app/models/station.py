import enum
import uuid
from sqlalchemy import String, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class StationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Station(Base):
    __tablename__ = "station"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    max_capacity_kw: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[StationStatus] = mapped_column(
        Enum(StationStatus), default=StationStatus.ACTIVE)
