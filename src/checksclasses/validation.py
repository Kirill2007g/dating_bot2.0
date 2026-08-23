import json
import redis

from aiogram.filters import BaseFilter
from aiogram.types import Message
from db.queries import check_city_in_db, save_in_city_mapping
from db.dadata_queries import check_in_dadata

from config import settings

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
                print("Город не найден Идем в dadata")
                check_dadata = await check_in_dadata(message.text)
                if check_dadata:
                    await save_in_city_mapping(message.text, check_dadata)
                    r.set(
                        city_key,
                        json.dumps({
                            "resolved_name": check_dadata
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



