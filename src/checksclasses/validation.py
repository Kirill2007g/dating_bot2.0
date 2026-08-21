from aiogram.filters import BaseFilter
from aiogram.types import Message
import asyncio

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
class IsValidCity(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return True


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