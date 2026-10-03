from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from src.checksclasses.decorators import ( track, track_message, ask,
                                           clear,  collect_selection,
                                           if_one_selected, if_multiple_selected)

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from src.handlers.keyboards import check_profiles, anketa_kb, anketa_kb_multiple, choose_gender, choose_looking_for, settings_kb, settings_kb_premium, settings_kb_language
from src.db.db_queries import get_profile, get_candidates, get_show_form, get_profile_media, get_profile_text
from src.states import StateMenu, StateRegistration
from src.checksclasses.validation import build_media_group
from aiogram.fsm.state import State
router = Router()
ANKETA_ACTIONS: dict[str, State] = {
    "Заполнить анкету заново": StateRegistration.name,
    "Изменить несколько пунктов": StateMenu.edit_multiple,
    "Изменить 'Имя'": StateRegistration.name,
    "Изменить 'Возраст'": StateRegistration.age,
    "Изменить 'Пол'": StateRegistration.gender,
    "Изменить 'Город'": StateRegistration.city,
    "Изменить 'О себе'": StateRegistration.description,
    "Изменить 'Кого вы ищете'": StateRegistration.looking_for,
    "Изменить 'Медиа'": StateRegistration.media,
}


@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext):
    if message.text == "Смотреть анкеты":
        profile = await get_show_form(tg_id=message.from_user.id)
        send = await get_candidates(profile)
        await message.answer(f"{send}")

    if message.text == "Мой профиль":
        await state.set_state(StateMenu.show_profile)
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
        await state.set_state(StateMenu.settings)
        await message.answer("Settings", reply_markup=settings_kb)

    if message.text == "Заполнить анкету заново":
        await message.answer("Выберите одно из:", reply_markup=anketa_kb)
        await state.set_state(StateMenu.anketa)
        logger.debug(f"словили message")

@router.message(StateMenu.settings, F.text == "Купить Премиум")
async def buy_premium(message: Message, state: FSMContext):
    await message.answer("Активируй Premium и будь в топе ✨""\n"
                         "\n"
                        "Выделяйся среди других:\n"
                        "📈 Больше показов анкеты\n"
                        "🚀 Больше лайков\n"
                        "👀 Твои лайки видят первыми\n"
                        "⭐️ Твоя анкета выше остальных\n"
                        "\n"
                        "Больше внимания. Больше взаимных. Больше знакомств 💫\n"
                        "\n"
                        "Выбери срок действия Premium:\n"
                        "\n"
                        "• 2 дня • ⭐ 150\n"
                        "\n"
                        "• 10 дней • ⭐ 350\n"
                        "\n"\
                        "• 30 дней • ⭐ 500\n"
                        "\n"
                        "• 90 дней • ⭐ 1000\n"
                        "\n"
                        "*Оплачивая Premium, ты принимаешь условия покупки", reply_markup=settings_kb_premium)

@router.message(StateMenu.settings, F.text == "Изменить язык")
async def change_language(message: Message, state: FSMContext):
    await message.answer("Languages available:", reply_markup=settings_kb_language)

prompts = {
        StateRegistration.name: "Как тебя зовут?",
        StateRegistration.age: "Сколько тебе лет?",
        StateRegistration.gender: "Укажи пол",
        StateRegistration.city: "В каком ты городе?",
        StateRegistration.description: "Расскажи о себе",
        StateRegistration.looking_for: "Кого ты ищешь?",
        StateRegistration.media: "Пришли фото или видео",
        StateRegistration.name: "Как тебя зовут?",
        StateMenu.edit_multiple: "Вам дан выбор из пунктов которые вы можете изменить" \
    ", отправляйте в чат по 1 пункту, а когда закончите нажмите на 'ВСЕ!'",
    }
keyboards = {
        StateMenu.edit_multiple: anketa_kb_multiple,
        StateRegistration.gender: choose_gender,
        StateRegistration.looking_for: choose_looking_for,
    }
@router.message(StateMenu.anketa, F.text.in_(ANKETA_ACTIONS.keys()))
# @if_one_selected
async def handle_actions(message: Message, state: FSMContext, bot: Bot):
    new_state = ANKETA_ACTIONS[message.text] #StateRegistration.name например
    # logger.debug(f"Словили actions, {new_state}")
    await state.update_data(is_single_edit=True)
    check_data = await state.get_data()
    print(f"[HANDLE_ACTIONS] Проверка записи FSM {check_data}")
    await state.set_state(new_state) #Теперь мы в состоянии StateRegistration.name
    check = keyboards.get(new_state, None)
    if check is None:
        await message.answer(prompts.get(new_state, "Не нашли промпт"))
    else:
        await message.answer(prompts.get(new_state, "Не нашли промпт"),
                             reply_markup=check) #Кидаем в чат промпт и клавиатуру, если она есть
    # await message.answer(prompts.get(new_state, "Не нашли промпт"),
    #                      reply_markup=keyboards.get(new_state, "Не нашли клавиатуру")) #Кидаем в чат промпт и клавиатуру, если она есть
    # await clear(message.chat.id, bot)

FIELD_ORDER_ = (StateRegistration.name, StateRegistration.age, StateRegistration.gender,
                 StateRegistration.city, StateRegistration.description, StateRegistration.looking_for,
                 StateRegistration.media)
anketa_actions_reverse = {v: k for k, v in ANKETA_ACTIONS.items()}
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
def map_sentences_to_states(sentences: list[str], actions: dict = ANKETA_ACTIONS):
    sentences_copy = sentences.copy()
    if 'ВСЕ!' in sentences_copy:
        sentences_copy.remove('ВСЕ!')
    states = [actions.get(sentence, sentence) for sentence in sentences_copy]
    states.sort(key=lambda state: FIELD_ORDER_.index(state) if state in FIELD_ORDER_ else 0)
    return states
@router.message(StateMenu.edit_multiple)
@track_message
@collect_selection
async def change_many_options_in_anketa(
    message: Message,
    state: FSMContext,
    bot: Bot,
    tracked_messages: list,
    selected_fields: list,
    finished: bool,
):
    if finished:
        if not selected_fields:
            await message.answer("Ты ничего не выбрал.Выбери хотя бы один пункт")
            await state.update_data(selected_fields=[])
            return
        mapped_states = map_sentences_to_states(selected_fields)
        new_state = mapped_states[0]
        await state.update_data(new_state=new_state)
        new_state_reply = prompts.get(new_state, "Не нашли соответствующее состояние")
        await message.answer(f"{new_state_reply}")
        return await message.answer(f"selected_fields: {selected_fields}\nMapped: {map_sentences_to_states(selected_fields)}")
        # mapped = map_sentences_to_states(selected_fields)
        # await message.answer(f"Mapped: {mapped}")
        # field_keys = [button_to_key[btn] for btn in selected_fields]
        # first_key, *rest = field_keys
        # await state.update_data(selected_fields=[], edit_queue=rest)
        # await state.set_state(FIELD_STATES[first_key])
        # await message.answer(FIELD_PROMPTS[first_key], reply_markup=ReplyKeyboardRemove())
        # return
    await message.answer(f"Пока выбрано: {selected_fields}", reply_markup=anketa_kb_multiple)


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
# FIELD_ORDER = {"name", "age", "gender",
#                "city", "description", "looking_for",
#                "media"}
# fsm_data_dict = {
#     "name": None,
#     "age": None,
#     "gender": None,
#     "city": None,
#     "description": None,
#     "looking_for": None,
#     "media": None,
# }
# FIELD_STATES = {
#     "name": StateRegistration.name,
#     "age": StateRegistration.age,
#     "gender": StateRegistration.gender,
#     "city": StateRegistration.city,
#     "description": StateRegistration.description,
#     "looking_for": StateRegistration.looking_for,
#     "media": StateRegistration.media,
# }
# dassdf = {
#     "name": "Изменить 'Имя'",
#     "age": "Изменить 'Возраст'",
#     "gender": "Изменить 'Пол'",
#     "city": "Изменить 'Город'",
#     "description": "Изменить 'О себе'",
#     "looking_for": "Изменить 'Кого вы ищете'",
#     "media": "Изменить 'Медиа'",
# }

# FIELD_PROMPTS = {
#     "name": "Как тебя зовут?",
#     "age": "Сколько тебе лет?",
#     "gender": "Укажи пол",
#     "city": "Теперь напиши свой город",
#     "description": "Теперь напишите о себе",
#     "looking_for": "Кого вы ищете",
#     "media": "Пришли фото/видео до 3 штук",
# }

# button_to_key = {v: k for k, v in dassdf.items()}
    pass