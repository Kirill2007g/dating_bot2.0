from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.states import StateMenu

from src.handlers.keyboards import check_profiles
router = Router()

@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext):
    if message.text == "Смотреть анкеты":
        await message.answer(f"❤️ - Лайк\n👎 - Дизлайк\n💌 - Лайк и сообщение\n💤 -  Назад", reply_markup=check_profiles)