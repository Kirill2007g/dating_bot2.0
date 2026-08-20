from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

import asyncio
from states import StateRegistration
from handlers.keyboards import(
    start_markup, choose_gender
)
from checksclasses.validation import (
    IsValidName, IsValidAge, IsValidCity,
    IsValidDescription, IsValidGender, IsValidLookingfor
)


router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)
    await state.set_state()



@router.message(F.text == "Заполнить анкету")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(StateRegistration.name)
    await message.answer("Как тебя зовут?")




@router.message(StateRegistration.name)
async def reg_name(message: Message, state: FSMContext):
    if not await IsValidName()(message):
        return await message.answer("Введи имя")
    await state.update_data(name=message.text)
    await state.set_state(StateRegistration.age)
    await message.answer("Сколько тебе лет")

@router.message(StateRegistration.age)
async def reg_age(message: Message, state: FSMContext):
    if not await IsValidAge()(message):
        return await message.answer("Введи возраст ")
    await state.update_data(age=message.text)
    await state.set_state(StateRegistration.gender)
    await message.answer("Теперь выберем пол", reply_markup=choose_gender)

@router.message(StateRegistration.gender)
async def reg_gender(message: Message, state: FSMContext):
    if not await IsValidGender()(message):
        return await message.answer("Выбери пол", reply_markup=choose_gender)
    await state.update_data(gender=message.text)
    await state.set_state(StateRegistration.city)
    await message.answer("Теперь напиши свой город")

@router.message(StateRegistration.city)
async def reg_city(message: Message, state: FSMContext):
    pass


@router.message(StateRegistration.description)
async def reg_description(message: Message, state: FSMContext):
    pass























# @router.message(StateRegistration.name)
# async def process_name(message: Message, state: FSMContext):

#     # Вызываем наш фильтр вручную прямо в условии!
#     if not await IsValidName()(message):
#         # Если фильтр вернул False — даем ошибку и стопаем выполнение
#         return await message.answer("Неверное имя! Только буквы, до 20 символов.")

#     # Если фильтр вернул True — код спокойно идет дальше
#     await state.update_data(name=message.text)
#     await message.answer("Принято! А теперь введи свой возраст числом:")
#     await state.set_state(StateRegistration.age)










