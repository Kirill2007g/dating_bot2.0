from src.db.models import CityMapping, User, Action
from sqlalchemy import func, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session
from sqlalchemy.dialects.postgresql import insert as pg_insert


async def check_city_in_db(user_text: str):
    clean_input = user_text.strip().lower()
    async with async_session() as session:
        query = select(CityMapping).where(CityMapping.user_input == clean_input)
        db_result = await session.execute(query)
        mapping = db_result.scalar_one_or_none()

        if mapping:
            print(f"\n[PostgreSQL] Найдено совпадение!")
            print(f"Пользователь ввел: {user_text}")
            print(f"Правильный город из БД: {mapping.resolved_name}")
            return mapping.resolved_name
        else:
            print(f"\n[PostgreSQL] В базе данных пусто для: '{user_text}'")
            return None

async def save_in_city_mapping(user_input: str, resolved_name: str):


    async with async_session() as session:
        query = insert(CityMapping).values(
            user_input=user_input.strip().lower(),
            resolved_name=resolved_name
        )

        await session.execute(query)
        await session.commit()

async def save_user_in_db(fsm_data):
    tg_id = fsm_data.get('tg_id')
    name = fsm_data.get('name')
    age = fsm_data.get('age')
    gender = fsm_data.get('gender')
    city = fsm_data.get('city')
    description = fsm_data.get('description')
    looking_for = fsm_data.get('looking_for')
    media_list = fsm_data.get('user_media_list', [])

    async with async_session() as session:
        try:
            new_user = User(
                tg_id=tg_id,
                name=name,
                age=age,
                gender=gender,
                city=city,
                description=description,
                looking_for=looking_for,
                user_media_list=media_list
            )
            session.add(new_user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"Ошибка БД: {e}")
            return False


async def get_profile(tg_id: int, n: int):
    async with async_session() as session:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        if n == 1:
            return user
        elif n == 0:
            return user.for_get_profile
        elif n == 3:
            return user.show_profile
        elif n == 4:
            return user.show_profile_media

async def get_profiles(sps: list):
    age = int(sps[0])
    city = sps[1]
    looking_for = sps[2]
    tg_id = int(sps[3])
    conv_age = list(range(age - 2, age + 3))
    async with async_session() as session:
        query = select(User).where(
            User.age.in_(conv_age),
            User.city == city,
            User.gender == looking_for
        ).order_by(
            func.abs(User.age - age),
            User.rating.desc()
        ).limit(1)
        result = await session.execute(query)
        return result.scalars().all()

async def gives_next_profile_tg_id(tg_id, n):
    get = await get_profile(tg_id, n)
    profile = await get_profiles(get)
    if not profile:
        return None
    tg_id = profile.tg_id
    return tg_id
async def set_reaction(from_user_id, to_user_id, reaction, message: str | None = None):
    async with async_session() as session:
        query = pg_insert(Action).values(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            reaction=reaction,
            message=message
        )
        query = query.on_conflict_do_update(
            constraint="uq_from_to_user",
            set_={"reaction": reaction, "message": message}
        )
        await session.execute(query)
        await session.commit()

async def adjust_rating(tg_id, rating_change: int):
    async with async_session() as session:
        query = update(User).where(User.tg_id==tg_id).values(rating=User.rating + rating_change)
        await session.execute(query)
        await session.commit()

async def likes_dislikes_ratio():
    pass

async def likes_matches_ratio():
    pass
# async def set_dislike():
#     pass
# async def set_like_with_message():
#     pass


# class ReactionType(str, Enum):
#     LIKE = "like"
#     DISLIKE = "dislike"

# class Action(Base):
#     __tablename__ = "actions"
#     __table_args__ = (
#         UniqueConstraint("from_user_id", "to_user_id", name="uq_from_to_user"),
#     )
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     from_user_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
#     )
#     to_user_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
#     )
#     reaction: Mapped[ReactionType] = mapped_column(nullable=False)
#     message: Mapped[str | None] = mapped_column(String(500), nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
#     from_user: Mapped['User'] = relationship(foreign_keys=[from_user_id])
#     to_user: Mapped['User'] = relationship(foreign_keys=[to_user_id])