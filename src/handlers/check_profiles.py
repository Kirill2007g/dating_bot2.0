from aiogram import Router, F
from src.states import StateMenu
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.keyboards import check_profiles_kb
from src.utils import add_reaction, get_next_profile

router = Router()







@router.message(StateMenu.check_profiles, F.text == "❤️")
async def cmd_like(message: Message, state: FSMContext):
    data = await state.get_data()
    ten_users_list = data.get("ten_users_list", [])
    from_user_id = data.get("from_user_id")
    to_user_id = data.get("to_user_id")
    tg_id = data.get("tg_id")

    await add_reaction(from_user_id=from_user_id, to_user_id=to_user_id, reaction="like")

    users, profiles, media_group, user = await get_next_profile(tg_id=tg_id, ten_users_list=ten_users_list)
    await message.answer_media_group(media_group)
    if user is not None:
        await message.answer(f"{user.name}, {user.age}, {user.city}\n{user.description}", reply_markup=check_profiles_kb)

@router.message(StateMenu.check_profiles, F.text == "👎")
async def cmd_dislike(message: Message, state: FSMContext):
    pass


@router.message(StateMenu.check_profiles, F.text == "💌")
async def cmd_like_and_message(message: Message, state: FSMContext):
    pass


