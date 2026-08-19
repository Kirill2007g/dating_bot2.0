from aiogram.filters import BaseFilter
from aiogram.types import Message
import asyncio

class IsValidName(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text.isalpha() and len(message.text) <= 20

class IsValidAge(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        age = int(message.text)
        return age.isdigit() and 16 < age < 130