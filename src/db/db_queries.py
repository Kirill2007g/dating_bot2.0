from src.db.models import CityMapping, MediaType, User, Action, UserMedia
from sqlalchemy import delete, func, select, insert, update
from src.db.database import async_session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload
import redis.asyncio as aioredis
from src.checksclasses.dictionaries import (ALLOWED_FIELDS, _MEDIA_TYPE_MAP,
                                            PROFILE_FIELDS, GENDER_MAP, GENDERS,
                                            )



class UserQueries:
    @classmethod
    async def save_user_in_db(cls, fsm_data):
        tg_id = fsm_data.get('tg_id')
        fields = {key: fsm_data.get(key) for key in PROFILE_FIELDS}
        media_list = fsm_data.get('user_media_list', [])

        async with async_session() as session:
            check_if_user_exists = await session.execute(
                select(User).where(User.tg_id == tg_id)
            )
            existing_user = check_if_user_exists.scalar_one_or_none()
            if existing_user:
                for field, value in fields.items():
                    setattr(existing_user, field, value)
                await session.execute(
                    delete(UserMedia).where(UserMedia.user_id == existing_user.id)
                )
                for media_item in media_list:
                    m_type = media_item.get("media_type")
                    f_id = media_item.get("file_id")
                    new_media = UserMedia(
                        user_id=existing_user.id,
                        media_type=_MEDIA_TYPE_MAP[m_type],
                        file_id=f_id,
                    )
                    session.add(new_media)
                await session.commit()
                return True
            try:
                db_media = []
                for media_item in media_list:
                    m_type = media_item.get("media_type")
                    f_id = media_item.get("file_id")
                    db_media.append(
                        UserMedia(
                            media_type=_MEDIA_TYPE_MAP[m_type],
                            file_id=f_id,
                        )
                    )
                new_user = User(
                    tg_id=tg_id,
                    **fields,
                    media=db_media
                )
                session.add(new_user)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                print(f"Ошибка БД: {e}")
                return False


    @classmethod
    async def update_user(cls, data: dict, flag_media: bool = False):
        tg_id = data.get('tg_id')
        if not tg_id:
            print("Ошибка: tg_id отсутствует в данных")
            return False
        if flag_media:
            async with async_session() as session:
                user_id = select(User.id).where(User.tg_id == tg_id)
                try:
                    for media_item in data['user_media_list']:
                        m_type = media_item.get("media_type")
                        f_id = media_item.get("file_id")
                        update_values_media = {
                            "media_type": m_type,
                            "file_id": f_id
                        }
                        media_query = (
                            update(UserMedia)
                            .where(UserMedia.user_id == user_id)
                            .values(**update_values_media)
                        )
                        await session.execute(media_query)
                        await session.commit()
                        return True
                except Exception as e:
                    await session.rollback()
                    print(f"Ошибка БД: {e}")
                    return False

        update_values = {
            key: value for key, value in data.items() if key in ALLOWED_FIELDS
            and value is not None
        }
        if not update_values:
            print("Нет данных для обновления")
            return True
        async with async_session() as session:
            try:
                query = (
                    update(User)
                    .where(User.tg_id == tg_id)
                    .values(**update_values)
                )
                await session.execute(query)
                await session.commit()
                print(f"Пользователь {tg_id} успешно обновлен. Изменены поля: {list(update_values.keys())}")
                return True
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при обновлении пользователя {tg_id} в БД: {e}")
                return False


    @classmethod
    async def update_media(cls,tg_id: int, media_list):
        async with async_session() as session:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            if user_id is None:
                return
            await session.execute(delete(UserMedia).where(UserMedia.user_id == user_id))
            session.add_all(UserMedia(user_id=user_id, **m)for m in media_list)
            await session.commit()


    @classmethod
    async def update_value(cls, tg_id: int, field: str, value: str | int):
        if field not in ALLOWED_FIELDS or not value:
            return False
        if field == "age":
            value = int(value)
        async with async_session() as session:
            query = update(User).where(User.tg_id == tg_id).values(**{field: value})
            await session.execute(query)
            await session.commit()


    @classmethod
    async def get_profile(cls, tg_id: int) -> User | None:
        async with async_session() as session:
            user_query = (
                select(User)
                .where(User.tg_id == tg_id)
                .options(selectinload(User.media))
            )
            user_result = await session.execute(user_query)
            return user_result.scalar_one_or_none()


    @classmethod
    async def get_show_form(cls, tg_id: int):
        user = await UserQueries.get_profile(tg_id)
        return user.show_form if user else None

    @classmethod
    async def get_profile_aclt(cls, tg_id: int):
        user = await UserQueries.get_profile(tg_id)
        return user.show_aclt if user else None

    @classmethod
    async def get_profile_media(cls, tg_id: int) -> list[UserMedia]:
        user = await UserQueries.get_profile(tg_id)
        if user is None:
            return []
        async with async_session() as session:
            user_query = (
                select(UserMedia)
                .where(UserMedia.user_id == user.id)
            )
            user_result = await session.execute(user_query)
            return list(user_result.scalars().all())

    @classmethod
    async def get_user_id(cls, tg_id: int) -> int | None:
        user = await UserQueries.get_profile(tg_id)
        return user.id if user else None





async def get_profiles_limit(age, city, looking_for, tg_id, seen_ids: list[int], limit: int=10) -> list[User]:
    age = int(age)
    city = city.strip()
    looking_for = looking_for.strip()
    tg_id = int(tg_id)
    if looking_for not in GENDERS:
        print(f"looking_for не в gender_map {looking_for}")
        return []
    looking_for_gender = GENDER_MAP[looking_for]
    age_range = range(age-2, age+3)
    async with async_session() as session:
        query = (
            select(User)
            .where(
                User.tg_id != tg_id,
                User.id.not_in(seen_ids),
                User.city == city,
                User.gender == looking_for_gender,
                User.age.in_(age_range))
            .options(selectinload(User.media))
        )   .order_by(func.abs(User.age-age),
            User.rating.desc()).limit(limit)
        result = await session.execute(query)
        profiles = result.scalars().all()
        return list(profiles)

#604800 = 7 дней
r = aioredis.Redis(host="localhost", port=6379, decode_responses=True)
async def add_to_seen_ids_table(user_tg_id: int, viewed_profile_id: int):
    redis_key = f"seen:{user_tg_id}"
    await r.sadd(redis_key, viewed_profile_id)
    await r.expire(redis_key, 604800)


async def get_all_seen_ids(user_tg_id: int) -> list[int]:
    redis_key = f"seen:{user_tg_id}"
    seen_ids_raw = await r.smembers(redis_key)
    return [int(x) for x in seen_ids_raw]





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