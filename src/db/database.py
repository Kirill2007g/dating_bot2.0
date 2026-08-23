from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings
from sqlalchemy import String, select



# Единственный Base на весь проект
class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.database_url, echo=True)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

