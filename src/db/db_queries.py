from src.db.models import CityMapping, User
from sqlalchemy import func, select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session



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

# async def get_profile(tg_id: int, boolean: bool) -> User | list | None:
#     async with async_session() as session:
#         query = select(User).where(User.tg_id == tg_id)
#         result = await session.execute(query)
#         user = result.scalar_one_or_none()
#         if user is None:
#             return None
#         if boolean:
#             return user
#         else:
#             return user.for_get_profile

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