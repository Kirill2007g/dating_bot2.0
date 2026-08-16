from pydantic import BaseModel, Field, ConfigDict
from .models import MediaType

class UserMediaBase(BaseModel):
    media_type: MediaType
    field_id: str = Field(..., max_length=255)


class UserMediaCreate(UserMediaBase):
    pass

class UserMediaResponse(UserMediaBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    tg_id:int
    username: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1000)
    age: int = Field(..., ge=14, le=130)
    city: str = Field(..., min_length=2, max_length=255)
    looked_for: str = Field(..., max_length=255)

class UserCreate(UserBase):
    pass  # Эту схему мы используем, когда бот получает данные из инпут-форм

class UserResponse(UserBase):
    id: int
    media: list[UserMediaResponse] = [] # Включаем связанные медиафайлы

    model_config = ConfigDict(from_attributes=True) # Важно для интеграции с SQLAlchemy