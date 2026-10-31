from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.db.models import MediaType


class UserBase(BaseModel):
    tg_id:int
    username: str = Field(..., max_length=255)
    age: int = Field(..., ge=14, le=130)
    gender: str
    city: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., max_length=1000)
    looking_for: str = Field(..., max_length=255)

    @field_validator('gender')
    def validate_gender(cls, value):
        if value not in ["Я Парень", "Я Девушка"]:
            raise ValueError("Нету такого варианта ответа")
        return value

    @field_validator('looking_for')
    def validate_looking_for(cls, value):
        if value not in ["Парни", "Девушки", "Без разницы"]:
            return ValueError("Нету такого варианта ответа")
        return value



class UserMediaBase(BaseModel):
    media_type: MediaType
    field_id: str = Field(..., max_length=255)


class UserMediaCreate(UserMediaBase):
    pass

class UserMediaResponse(UserMediaBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    media: list[UserMediaResponse] = []

    model_config = ConfigDict(from_attributes=True)