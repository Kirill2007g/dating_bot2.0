from src.db.models import CityMapping, User, Action, SeenProfiles
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

async def get_profile(tg_id: int) -> User | None:
    async with async_session() as session:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def get_show_form(tg_id: int):
    user = await get_profile(tg_id)
    return user.show_form if user else None

async def get_profile_text(tg_id: int):
    user = await get_profile(tg_id)
    return user.show_profile if user else None

async def get_profile_media(tg_id: int):
    user = await get_profile(tg_id)
    return user.show_profile_media if user else None

# async def get_next_profile(tg_id: int, _dictionary_: dict) -> dict | None:


# async def set_reaction(from_user_id, to_user_id, reaction, message: str | None = None):
#     async with async_session() as session:
#         query = pg_insert(Action).values(
#             from_user_id=from_user_id,
#             to_user_id=to_user_id,
#             reaction=reaction,
#             message=message
#         )
#         query = query.on_conflict_do_update(
#             constraint="uq_from_to_user",
#             set_={"reaction": reaction, "message": message}
#         )
#         await session.execute(query)
#         await session.commit()

# async def adjust_rating(tg_id, rating_change: int):
#     async with async_session() as session:
#         query = update(User).where(User.tg_id==tg_id).values(rating=User.rating + rating_change)
#         await session.execute(query)
#         await session.commit()

# async def likes_dislikes_ratio():
#     pass

# async def likes_matches_ratio():
#     pass

async def mark_profile_seen(viewer_tg_id: int,seen_tg_id: int) -> None:
    async with async_session() as session:
        query = pg_insert(SeenProfiles).values(
            viewer_tg_id=viewer_tg_id,
            seen_tg_id=seen_tg_id
        ).on_conflict_do_nothing(index_elements=["viewer_tg_id" "seen_tg_id"])
        await session.execute(query)
        await session.commit()

async def get_candidates(spisok: list,limit: int = 30,) -> dict:
    age = int(spisok[0])
    city = spisok[1]
    looking_for = spisok[2]
    tg_id = int(spisok[3])
    age_range = range(age-2, age+2)
    async with async_session() as session:
        seen_subq = select(SeenProfiles.seen_tg_id).where(
            SeenProfiles.viewer_tg_id == tg_id
        )
        query = select(User).where(
            User.age.in_(age_range),
            User.city == city,
            User.gender == looking_for,
            User.tg_id != tg_id,
            User.tg_id.notin_(seen_subq)
        ).order_by(func.abs(User.age - age),
         User.rating.desc()).limit(limit)
        result = await session.execute(query)
        profiles = result.scalars().all()

        return {
            str(user.tg_id): {
                "id": user.id,
                "tg_id": user.tg_id,
                "name": user.name,
                "age": user.age,
                "gender": user.gender,
                "city": user.city,
                "description": user.description,
                "looking_for": user.looking_for,
                "rating": user.rating,
            }
            for user in profiles
        }
# async def get_user_for_show_ankets(_list_: list, seen_tg_ids: list) -> dict:
#     tg_id = int(_list_[3])
#     age = int(_list_[0])
#     city = _list_[1]
#     looking_for = _list_[2]
#     age_range = list(range(age - 2, age + 3))
#     async with async_session() as session:
#         filters = [
#             User.age.in_(age_range),
#             User.city == city,
#             User.gender == looking_for,
#             User.tg_id != tg_id
#         ]
#         if seen_tg_ids:
#             filters.append(~User.tg_id.notin_(seen_tg_ids))
#         query = select(User).where(*filters).order_by(
#             func.abs(User.age - age),
#             User.rating.desc(). limit(30))
#         result = await session.execute(query)
#         profiles = result.scalars().all()
#         profiles_dict = {
#             str(user.tg_id): {
#                 "id": user.id, #int
#                 "tg_id": user.tg_id, #int
#                 "name": user.name, #str
#                 "age": user.age, #int
#                 "gender": user.gender, #str
#                 "city": user.city, #str
#                 "description": user.description, #str
#                 "looking_for": user.looking_for, #str
#                 "rating": user.rating, #Decimal
#             }
#             for user in profiles
#         }
#         return profiles_dict

lst = {
    "id": 5, #int
    "tg_id": 7654337654, #int
    "name": "Kacob", #str
    "age": 18, #int
    "gender": "male", #str
    "city": "Kiev", #str
    "description": "scientist", #str
    "looking_for": "female", #str
    "rating": 5.0001, #Decimal
}

dct = {
    "id": ..., #int
    "tg_id": ..., #int
    "name": ..., #str
    "age": ..., #int
    "gender": ..., #str
    "city": ..., #str
    "description": ..., #str
    "looking_for": ..., #str
    "rating": ..., #Decimal
}
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