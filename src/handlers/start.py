import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router

router = Router()

@router.message()
async def start_message(message: Message):
    await message.answer("Привет я бот для поиска пары!")


