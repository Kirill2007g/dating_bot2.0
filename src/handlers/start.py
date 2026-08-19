import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F
from handlers.keyboards import start_markup
from aiogram.fsm.context import FSMContext
from states import StateRegistration


router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)
    await state.set_state()



@router.message(F.text == "Заполнить анкету")
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Отлично, Как тебя зовут?")



@router.message(StateRegistration.name)
async def reg_age(message: Message, state: FSMContext):
    pass