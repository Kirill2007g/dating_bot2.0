import json
from typing import Any, Awaitable, Callable
import asyncio
import redis
from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, Message
from aiogram.fsm.context import FSMContext

from src.config import settings
from src.db.db_queries import check_city_in_db, save_in_city_mapping
from src.db.validation_queries import validate_city_geopy

dadata_api_key = settings.dadata_api_key.get_secret_value()
dadata_secret_key = settings.dadata_secret_key.get_secret_value()

class IsValidName(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return message.text.isalpha() and len(message.text) <= 20

class IsValidAge(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text or not message.text.isdigit():
            return False
        age = int(message.text)
        return age.is_integer() and 16 <= age <= 130

class IsValidGender(BaseFilter): #Парни, Девушки, Без разницы
    async def __call__(self, callback_query: CallbackQuery) -> bool:
        if not callback_query.data:
            return False
        available_options = ["gender_male", "gender_female"]
        return callback_query.data in available_options


# временно
#Проблема с dadata киев = киевское шоссе москва, хотя должно быть городом проблема в clean
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
class IsValidCity(BaseFilter):
    """Проверка города на валидность,
    1. Смотрим в кеше(Redis)
    2. Идём в бд если не нашли в кеше
    3. Если нашли в бд записываем в кеш
    4. Если не нашли то"""
    async def __call__(self, message: Message) -> bool:
        city = message.text.strip()
        city_key = f"city:{city.lower()}"
        cached_data = r.get(city_key)
        if cached_data:
            result = json.loads(cached_data)
            print("Город найден в Redis")
            print(f"Нормальный вид: {result['resolved_name']}")
            return True
        else:
            print("В Redis пусто, переходим к бд")
            check_db = await check_city_in_db(city)
            if check_db:
                print("Сохраняем город в Redis")
                r.set(
                    city_key, json.dumps(
                        {"resolved_name": check_db}
                    )
                )
                return True
            else:
                print("Город не найден Идем в geopy")
                check_geopy = await validate_city_geopy(city)
                if check_geopy:
                    city_name = check_geopy.raw.get('name') or check_geopy.address.split(',')[0]
                    await save_in_city_mapping(city, city_name)
                    r.set(
                        city_key,
                        json.dumps({
                            "resolved_name": check_geopy.address
                        }),
                        ex=60*60*24*30
                    )
                    return True
                else:
                    print("Нигде ничего не нашли")
                    return False


# временно
class IsValidDescription(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # if not message.text:
        #     return False
        # description = message.text
        # return not len(description) > 1000
        return True

class IsValidLookingfor(BaseFilter):
    async def __call__(self, callback_query: CallbackQuery) -> bool:
        if not callback_query.data:
            return False
        available_options = ["looking_for_men", "looking_for_women", "looking_for_any"]
        return callback_query.data in available_options

def build_media_group(media_list: list) -> list:
    result = []
    for item in media_list:
        if isinstance(item, dict):
            m_type = item.get("type") or item.get("media_type")
            f_id = item.get("file_id")
        else:
            m_type = item.media_type.value if hasattr(item.media_type, 'value') else item.media_type
            f_id = item.file_id
        if m_type:
            m_type = m_type.lower()
        if m_type in ("photo", "photo"):
            result.append(InputMediaPhoto(media=f_id))
        elif m_type in ("video", "video_note", "circle"):
            result.append(InputMediaVideo(media=f_id))

    return result

class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.2):
        self.latency = latency
        self.album_data: dict[str, list[Message]] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        if not event.media_group_id:
            if event.photo or event.video or event.video_note:
                data["user_media"] = self._extract_media([event])
            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
            return
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            album_messages = self.album_data.pop(event.media_group_id)
            data["user_media"] = self._extract_media(album_messages)
        return await handler(event, data)
    @staticmethod
    def _extract_media(messages: list[Message]) -> list[dict]:
        user_media = []
        for msg in messages:
            if msg.photo:
                photo = msg.photo[-1]
                user_media.append({"media_type": "PHOTO", "file_id": photo.file_id})
            elif msg.video:
                user_media.append({"media_type": "VIDEO", "file_id": msg.video.file_id})
            elif msg.video_note:
                user_media.append({"media_type": "VIDEO_NOTE", "file_id": msg.video_note.file_id})
        return user_media

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        state: FSMContext = data.get("state")
        if state:
            current_state = await state.get_state()
            logger.info(f"Текущий State {current_state}")
        return await handler(event, data)