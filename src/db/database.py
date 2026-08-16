from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

# Единственный Base на весь проект
class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, echo=True)
