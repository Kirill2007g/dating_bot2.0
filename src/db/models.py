from enum import Enum
from decimal import Decimal
from sqlalchemy import JSON, BigInteger, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base

class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    NOTE = "note"

class UserMedia(Base):
    __tablename__ = "user_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(String(50), nullable=False)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="media")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    looking_for: Mapped[str] = mapped_column(String(255), nullable=False)
    user_media_list: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    # rating: Mapped[Decimal] = mapped_column(
    #     Numeric(precision=10, scale=4),
    #     default=Decimal("0.0000"),
    #     server_default="0.0000"
    # )


    media: Mapped[list["UserMedia"]] = relationship(
        "UserMedia",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class CityMapping(Base):
    __tablename__ = "city_mapping"

    user_input: Mapped[str] = mapped_column(String(100), nullable=False, primary_key=True)
    resolved_name: Mapped[str] = mapped_column(String(100), nullable=False)

class Cities(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)