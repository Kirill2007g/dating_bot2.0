import json

from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
import redis

from sqlalchemy import select
from src.db.database import async_session
from src.db.models import CityMapping


async def validate_city_geopy(user_input):
    async with Nominatim(
            user_agent="MyCisCityValidatorApp/1.0 (screenasol@gmail.com)",
            adapter_factory=AioHTTPAdapter
    ) as geocoding:
        try:
            location = await geocoding.geocode(
                user_input,
                exactly_one=True,
                language="ru"
            )
            return location
        except Exception as e:
            print(f"Ошибка при обращении к geopy: {e}")
            return None



























# nominatim_api_key = None
# url_nominatim = "https://nominatim.openstreetmap.org/search?<city>"

# api_key = settings.dadata_api_key.get_secret_value()
# # secret_key = settings.dadata_secret_key.get_secret_value()
# async def check_in_dadata(user_input: str):
#     url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "Authorization": f"Token {api_key}"
#     }
#     data = {
#         "query": user_input,
#         "count": 1,
#         "from_bound": {"value": "city"},
#         "to_bound": {"value": "city"}
#     }
#     response = requests.post(url=url, headers=headers, json=data)
#     if response.status_code == 200:
#         result = response.json()
#         suggestions = result.get("suggestions", [])
#         if not suggestions:
#             print("Dadata ничего не нашла")
#             return None
#         city = suggestions[0]['value']
#         print(f"Dadata нашла: {city}")
#         return city
#     else:
#         print("Ошибка dadata")
#         return None



# import httpx
# import asyncio

# async def validate_city_nominatim(city_name: str) -> dict | None:
#     # Nominatim требует уникальный User-Agent для защиты от спама
#     headers = {"User-Agent": "MyCisCityValidatorApp/1.0 (screenasol@gmail.com)"}

#     # Параметры запроса: ищем только города (featuretype=settlement)
#     # и ограничиваем выдачу 1 результатом
#     params = {
#         "q": city_name,
#         "format": "json",
#         "limit": 1,
#         "featuretype": "settlement"
#     }

#     url = "https://openstreetmap.org"

#     # Используем асинхронный клиент
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(url, params=params, headers=headers)
#             response.raise_for_status()
#             data = response.json()

#             if data:
#                 return data[0]  # Возвращаем первый найденный объект
#             return None  # Город не найден

#         except httpx.HTTPError as e:
#             print(f"Ошибка запроса: {e}")
#             return None