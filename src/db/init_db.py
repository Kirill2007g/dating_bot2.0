import asyncio
from src.db.database import Base, engine
from src.db import models
from sqlalchemy import text


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS user_media CASCADE"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы!")


if __name__ == "__main__":
    asyncio.run(init_db())

