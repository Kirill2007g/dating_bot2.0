from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


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
    rating: Mapped[Decimal] = mapped_column(
         Numeric(precision=10, scale=4),
         default=Decimal("0.0000"),
         server_default="0.0000",
         nullable=False
    )
    @property
    def for_get_profile(self):
        return [self.age, self.city, self.looking_for, self.tg_id]

    @property
    def show_profile(self):
        return f"{self.name}, {self.age}, {self.city}"

    @property
    def show_profile_media(self):
        return self.user_media_list

    def __repr__(self):
        return (f"<User:\n"
                f" ID:{self.id}\n TG_ID:{self.tg_id}\n NAME:{self.name}\n"
                f"AGE:{self.age}\n GENDER:{self.gender}\n CITY:{self.city}\n "
                f"DESCRIPTION:{self.description}\n LOOKING_FOR:{self.looking_for}\n"
                f" MEDIA_LIST:{self.user_media_list}\n RATING:{self.rating}\n>")



class CityMapping(Base):
    __tablename__ = "city_mapping"

    user_input: Mapped[str] = mapped_column(String(100), nullable=False, primary_key=True)
    resolved_name: Mapped[str] = mapped_column(String(100), nullable=False)

class Cities(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

class ReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class Action(Base):
    __tablename__ = "actions"
    __table_args__ = (
        UniqueConstraint("from_user_id", "to_user_id", name="uq_from_to_user"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reaction: Mapped[ReactionType] = mapped_column(nullable=False)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    from_user: Mapped['User'] = relationship(foreign_keys=[from_user_id])
    to_user: Mapped['User'] = relationship(foreign_keys=[to_user_id])