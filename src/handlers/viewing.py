from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from src.checksclasses.decorators import track, track_message, ask, clear

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from src.handlers.keyboards import check_profiles, anketa_kb, anketa_kb_multiple
from src.db.db_queries import get_profile, get_candidates, get_show_form, get_profile_media, get_profile_text
from src.states import StateMenu, StateRegistration
from src.checksclasses.validation import build_media_group
from aiogram.fsm.state import State
router = Router()
ANKETA_ACTIONS: dict[str, State] = {
    "Заполнить анкету заново": StateRegistration.make_anketa_again,
    "Изменить несколько пунктов": StateMenu.edit_multiple,
    "Изменить 'Имя'": StateRegistration.name,
    "Изменить 'Возраст'": StateRegistration.age,
    "Изменить 'Пол'": StateRegistration.gender,
    "Изменить 'Город'": StateRegistration.city,
    "Изменить 'О себе'": StateRegistration.description,
    "Изменить 'Кого вы ищете'": StateRegistration.looking_for,
    "Изменить 'Медиа'": StateRegistration.media,
}

fsm_data_dict = {
    "name": None,
    "age": None,
    "gender": None,
    "city": None,
    "description": None,
    "looking_for": None,
    "media": None,
}

dassdf = {
    "name": "Изменить Имя",
    "age": "Изменить Возраст",
    "gender": "Изменить Пол",
    "city": "Изменить Город",
    "description": "Изменить О себе",
    "looking_for": "Изменить Кого вы ищете",
    "media": "Изменить Медиа",
}

button_to_key = {v: k for k, v in dassdf.items()}

def process_selection(user_message: str, data: dict):
    if user_message == "ВСЕ!":
        print("Выбор завершен! Итоговый словарь:", data)
        return False

    if user_message in button_to_key:
        key = button_to_key[user_message]
        data[key] = True
        print(f"Поле {key} отмечено как True")
    return True

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

    if message.text == "Настройки":
        await message.answer("Settings")

    if message.text == "Заполнить анкету заново":
        await message.answer("Выберите одно из:", reply_markup=anketa_kb)
        await state.set_state(StateMenu.anketa)
        logger.debug(f"словили message")





@router.message(StateMenu.anketa, F.text.in_(ANKETA_ACTIONS.keys()))
async def handle_actions(message: Message, state: FSMContext, bot: Bot):
    new_state = ANKETA_ACTIONS[message.text]
    logger.debug(f"Словили actions, {new_state}")
    await state.set_state(new_state)
    prompts = {
        StateRegistration.name: "Как тебя зовут?",
        StateRegistration.age: "Сколько тебе лет?",
        StateRegistration.gender: "Укажи пол",
        StateRegistration.city: "В каком ты городе?",
        StateRegistration.description: "Расскажи о себе",
        StateRegistration.looking_for: "Кого ты ищешь?",
        StateRegistration.media: "Пришли фото или видео",
        StateRegistration.make_anketa_again: "Как тебя зовут?",
        StateMenu.edit_multiple: "Вам дан выбор из пунктов которые вы можете изменить" \
    ", отправляйте в чат по 1 пункту, а когда закончите нажмите на 'ВСЕ!'",
    }
    keyboards = {
        StateMenu.edit_multiple: anketa_kb_multiple,
    }
    await message.answer(prompts.get(new_state, "Продолжаем..."), reply_markup=keyboards.get(new_state))
    await clear(message.chat.id, bot)


@router.message(StateMenu.edit_multiple)
@track_message
async def change_many_options_in_anketa(message: Message, state: FSMContext, bot: Bot, tracked_messages: list[int]):
    await process_selection(user_message=message.text, data=fsm_data_dict)
    await message.answer("+1", reply_markup=anketa_kb_multiple)
    await message.answer(f"ЗАТРЕКАНЫ: {tracked_messages}")


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