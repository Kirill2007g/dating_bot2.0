from src.db.models import CityMapping, MediaType, User, Action, SeenProfiles, UserMedia
from sqlalchemy import delete, func, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import selectinload
import redis.asyncio as aioredis
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

_MEDIA_TYPE_MAP = {
                "PHOTO": MediaType.PHOTO,
                "VIDEO": MediaType.VIDEO,
                "VIDEO_NOTE": MediaType.CIRCLE,
            }
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
        check_existing_user = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        existing_user = check_existing_user.scalar_one_or_none()
        if existing_user:
            existing_user.name = name
            existing_user.age = age
            existing_user.gender = gender
            existing_user.city = city
            existing_user.description = description
            existing_user.looking_for = looking_for
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
                name=name,
                age=age,
                gender=gender,
                city=city,
                description=description,
                looking_for=looking_for,
                media=db_media
            )
            session.add(new_user)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"Ошибка БД: {e}")
            return False


async def update_user(data: dict, flag_media: bool = False):
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

    allowed_columns = {"name", "age", "gender", "city", "description", "looking_for"}
    update_values = {
        key: value for key, value in data.items() if key in allowed_columns
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

async def get_profile(tg_id: int) -> User | None:
    async with async_session() as session:
        user_query = (
            select(User)
            .where(User.tg_id == tg_id)
            .options(selectinload(User.media))
        )
        user_result = await session.execute(user_query)
        return user_result.scalar_one_or_none()

async def get_show_form(tg_id: int):
    user = await get_profile(tg_id)
    return user.show_form if user else None


async def get_profile_aclt(tg_id: int):
    user = await get_profile(tg_id)
    return user.show_aclt if user else None

async def get_profile_media(tg_id: int) -> list[UserMedia]:
    user = await get_profile(tg_id)
    if user is None:
        return []
    async with async_session() as session:
        user_query = (
            select(UserMedia)
            .where(UserMedia.user_id == user.id)
        )
        user_result = await session.execute(user_query)
        return list(user_result.scalars().all())
# async def get_profile_media(tg_id: int):
#     user = await get_profile(tg_id)
#     user_id = user.show_userid
#     async with async_session() as session:
#         user_query = (
#             select(UserMedia)
#             .where(UserMedia.id == user_id)

#         )
#         user_result = await session.execute(user_query)
#         return user_result
#     # return UserMedia.return_user_media if user else None



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




GENDER_MAP = {
    'looking_for_male': 'gender_male',
    'looking_for_female': 'gender_female',
    'looking_for_any': None
}
GENDERS = ['gender_male', 'gender_female', 'looking_for_male', 'looking_for_female', 'looking_for_any']
async def get_ten(age, city, looking_for, tg_id, seen_ids: list[int], limit: int=10):
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
        return profiles

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
