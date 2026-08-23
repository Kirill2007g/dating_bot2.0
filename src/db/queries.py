from db.models import CityMapping
from sqlalchemy import select, insert
from db.database import async_session

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
