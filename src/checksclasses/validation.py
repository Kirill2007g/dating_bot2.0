import json
from typing import Any, Awaitable, Callable, Dict, List
import asyncio
import redis
from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import InputMediaPhoto, InputMediaVideo, Message, TelegramObject
from aiogram.dispatcher.flags import get_flag

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
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        available_options = ["Я Парень", "Я Девушка"]
        return message.text in available_options


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
            check_db = await check_city_in_db(message.text)
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
                check_geopy = await validate_city_geopy(message.text)
                if check_geopy:
                    city_name = check_geopy.raw.get('name') or check_geopy.address.split(',')[0]
                    await save_in_city_mapping(message.text, city_name)
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
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        available_options = ["Парни", "Девушки", "Без разницы"]
        return message.text in available_options


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.2):
        self.latency = latency
        self.storage: Dict[str, List[Message]] = {}
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        album_flag = get_flag(data, "album")
        if not album_flag:
            return await handler(event, data)
        if not event.media_group_id:
            data["album"] = [event]
            return await handler(event, data)
        mid = event.media_group_id
        if mid not in self.storage:
            self.storage[mid] = []
            self.storage[mid].append(event)
            await asyncio.sleep(self.latency)
            data["album"] = self.storage.pop(mid, [])
            if not data["album"]:
                return
            return await handler(event, data)
        else:
            self.storage[mid].append(event)
            return

def build_media_group(media_list: list[dict]):
    result = []
    for item in media_list:
        if item["type"] == "photo":
            result.append(InputMediaPhoto(media=item["file_id"]))
        elif item["type"] == "video":
            result.append(InputMediaVideo(media=item["file_id"]))
    return result