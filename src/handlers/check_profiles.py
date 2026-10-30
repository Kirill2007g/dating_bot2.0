from aiogram import Router, F
from src.states import StateMenu
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
router = Router()


@router.message(StateMenu.check_profiles)
async def check_profiles(message: Message, state: FSMContext):
    pass

@router.message(StateMenu.check_profiles, F.text == "❤️")
async def cmd_like(message: Message, state: FSMContext):
    pass


@router.message(StateMenu.check_profiles, F.text == "👎")
async def cmd_dislike(message: Message, state: FSMContext):
    pass


@router.message(StateMenu.check_profiles, F.text == "💌")
async def cmd_like_and_message(message: Message, state: FSMContext):
    pass


