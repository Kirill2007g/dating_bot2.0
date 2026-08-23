
from config import settings
import requests




api_key = settings.dadata_api_key.get_secret_value()
secret_key = settings.dadata_secret_key.get_secret_value()
async def check_in_dadata(user_input: str):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {api_key}"
    }
    data = {
        "query": user_input,
        "count": 1
    }
    response = requests.post(url=url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        suggestions = result.get("suggestions", [])
        if not suggestions:
            print("Dadata ничего не нашла")
            return None
        city = suggestions[0]['value']
        print(f"Dadata нашла: {city}")
        return city
    else:
        print("Ошибка dadata")
        return None