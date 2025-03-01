import uuid
from typing import Optional
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(
        String, nullable=True)  # Para usuarios SSO
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # For SSO
    google_id: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True)
    microsoft_id: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=True)
