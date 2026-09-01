from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.handlers.keyboards import check_profiles
from src.db.db_queries import get_profile, get_profiles, set_reaction, gives_next_profile_tg_id
from src.states import StateMenu, StateRegistration
from src.checksclasses.validation import build_media_group

router = Router()

@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext):
    if message.text == "Смотреть анкеты":
        profile = await get_profile(tg_id=message.from_user.id, n=0)
        send = await get_profiles(profile)
        await message.answer(f"{send}", reply_markup=check_profiles)

    if message.text == "Мой профиль":
        profile = await get_profile(tg_id=message.from_user.id, n=3)
        media_list = await get_profile(tg_id=message.from_user.id, n=4)
        if media_list:
            media = build_media_group(media_list)
            await message.answer_media_group(media=media)
        await message.answer(profile)


    if message.text == "Заполнить анкету заново":
        await state.set_state(StateRegistration.name)
        await message.answer("Как тебя зовут?")



    if message.text == "Настройки":
        await message.answer("Settings")


@router.message(F.text == "❤️")
async def like_profile(message: Message, state: FSMContext):
    profile = await get_profile(tg_id=message.from_user.id, n=0)
    to_user_id = await gives_next_profile_tg_id(tg_id=message.from_user.id, n=0)
    await set_reaction(
        from_user_id=message.from_user.id,
        to_user_id=to_user_id,
        reaction="like",
        message=None,

    )

# @router.message(F.text == "👎")
# async def dislike_profile(message: Message, state: FSMContext):
#     profile = await get_profile(tg_id=message.from_user.id, n=0)
#         await set_reaction(
#             from_user_id=message.from_user.id,
#             to_user_id=,
#             reaction="like"
#             message=None,

#         )
# @router.message(F.text == "💌")
# async def like_and_text_profile(message: Message, state: FSMContext):
#     profile = await get_profile(tg_id=message.from_user.id, n=0)
#         await set_reaction(
#             from_user_id=message.from_user.id,
#             to_user_id=,
#             reaction="like"
#             message=None,

#         )
@router.message(F.text == "💤")
async def go_back(message: Message, state: FSMContext):
    pass