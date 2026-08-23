import asyncio
from db.database import Base, engine
import db.models  # noqa: F401 — регистрирует модели в Base.metadata


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы!")


if __name__ == "__main__":
    asyncio.run(init_db())