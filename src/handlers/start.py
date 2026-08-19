import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F
from handlers.keyboards import start_markup



router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)



# @router.message(F.text == "Заполнить анкету")
# async def start_registration(message: Message):
#     pass