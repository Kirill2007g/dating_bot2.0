import asyncio
from decimal import Decimal
from src.db.database import async_session
from src.db.models import User


async def fill_db():
    async with async_session() as session:
        base_rating = Decimal("5.0000")
        ages = [24, 23, 26, 27]

        users = [
            User(
                tg_id=100000 + i,
                name=f"User{i}",
                age=ages[i % len(ages)],
                gender="male" if i % 2 == 0 else "female",
                city="Odesa",
                description=f"Test user number {i}",
                looking_for="female" if i % 2 == 0 else "male",
                user_media_list=[],
                rating=base_rating + Decimal("0.0001") * i,
            )
            for i in range(1, 51)
        ]

        session.add_all(users)
        await session.commit()
        print(f"{len(users)} пользователей добавлено!")


if __name__ == "__main__":
    asyncio.run(fill_db())