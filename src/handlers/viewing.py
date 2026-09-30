from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.handlers.keyboards import check_profiles
from src.db.db_queries import get_profile, get_candidates, get_show_form, get_profile_media, get_profile_text
from src.states import StateMenu, StateRegistration
from src.checksclasses.validation import build_media_group

router = Router()

@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext):
    if message.text == "Смотреть анкеты":
        profile = await get_show_form(tg_id=message.from_user.id)
        send = await get_candidates(profile)
        await message.answer(f"{send}")

    if message.text == "Мой профиль":
        profile_text = await get_profile_text(message.from_user.id)
        profile_media = await get_profile_media(message.from_user.id)
        if profile_media:
            media_list = [
                {"type": m.media_type.value, "file_id": m.file_id}
                for m in profile_media
            ]
            media_group = build_media_group(media_list)
            if media_group:
                await message.answer_media_group(media_group)
        await message.answer(profile_text)


    if message.text == "Заполнить анкету заново":
        await state.set_state(StateRegistration.name)
        await message.answer("Как тебя зовут?")



    if message.text == "Настройки":
        await message.answer("Settings")


@router.message(F.text == "❤️")
async def like_profile(message: Message, state: FSMContext):
    profile = await get_profile(tg_id=message.from_user.id)
    to_user_id = await gives_next_profile_tg_id(tg_id=message.from_user.id)
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