from enum import Enum
from sqlalchemy import BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

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
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    looked_for: Mapped[str] = mapped_column(String(255), nullable=False)

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