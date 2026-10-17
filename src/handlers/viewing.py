from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from src.db.db_queries import get_ten
from src.checksclasses.decorators import ( track, track_message, ask,
                                           clear,
                                           if_one_selected)
from src.checksclasses.dictionaries import (ANKETA_ACTIONS, prompts, keyboards,
                                      FIELD_ORDER_)
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from src.handlers.keyboards import (check_profiles as check_profiles_kb, anketa_kb, choose_gender,
                                     choose_looking_for, settings_kb, settings_kb_premium,
                                       settings_kb_language, menu_kb, zzz_kb)
from src.db.db_queries import (get_profile, get_candidates, get_show_form,
                                get_profile_media, get_profile_aclt)
from src.states import StateMenu, StateRegistration
from src.checksclasses.validation import LoggingMiddleware, build_media_group
from aiogram.fsm.state import State
router = Router()
router.message.middleware(LoggingMiddleware())


@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext):
    if not message.text:
        return
    if message.text == "Смотреть анкеты":
        await message.answer("Смотреть анкеты!!!")
        # await state.set_state(StateMenu.check_profiles)
        # #Берем user_aclt
        # if message.from_user is None:
        #     return
        # user_profile = await get_profile(tg_id=message.from_user.id)
        # if user_profile is None:
        #     await message.answer("Анкета не найдена")
        #     return
        # user_aclt = await get_profile_aclt(tg_id=message.from_user.id)
        # if user_aclt is None:
        #     await message.answer("Юзер aclt не найден")
        #     return
        # age, city, looking_for, tg_id = user_aclt



        # await state.set_state(StateMenu.check_profiles)
        if message.from_user is None:
                    return
        user_profile = await get_profile(tg_id=message.from_user.id)
        await message.answer("ВЗЯЛИ ПРОФИЛЬ")
        if user_profile is None:
            await message.answer("Анкета не найдена.")
            return
        user_aclt = await get_profile_aclt(user_profile.tg_id)
        await message.answer("взяли aclt")
        if user_aclt is None:
            await message.answer("Анкета не найдена.")
            return
        age, city, looking_for, tg_id = user_aclt
        await message.answer(f"age: {age} city: {city} looking_for: {looking_for} tg_id: {tg_id}")
        profiles = await get_ten(age, city, looking_for, tg_id)
        await message.answer("УСПЕХ GET TEN")
        if not profiles:
            await message.answer("анкет по критериям не нашли")
            return
        for user in profiles:
            text =(
            f"User \n"
            f"ID: {user.id}\n"
            f"NAME: {user.name}\n"
            f"AGE: {user.age}\n"
            f"CITY: {user.city}"
            f"looking_for: {user.looking_for}\n"
            f"gender: {user.gender}\n\n"
            f"Media\n"
            f"MEDIA_TYPE: {user.media}")

            await message.answer(text)
        # if message.from_user is None:
        #     return


    if message.text == "Мой профиль":
        if message.from_user is None:
            return
        profile_text = await get_profile_aclt(message.from_user.id)
        profile_media = await get_profile_media(message.from_user.id)
        if profile_media:
            media_list = [
                {"type": m.media_type.value, "file_id": m.file_id}
                for m in profile_media
            ]
            media_group = build_media_group(media_list)
            if media_group:
                await message.answer_media_group(media_group)
        if profile_text is not None:
            await message.answer(profile_text, reply_markup=menu_kb)

    if message.text == "Настройки":
        await state.set_state(StateMenu.settings)
        await message.answer("Settings", reply_markup=settings_kb)

    if message.text == "Заполнить анкету заново":
        await message.answer("Выберите одно из:", reply_markup=anketa_kb)
        await state.set_state(StateMenu.anketa)
        # logger.debug(f"словили message")


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

@router.message(StateMenu.anketa, F.text.in_(ANKETA_ACTIONS.keys()))
async def handle_actions(message: Message, state: FSMContext, bot: Bot):
    if message.text is None:
        return
    if message.text == "Заполнить анкету заново":
        await state.set_state(StateRegistration.name)
        await message.answer("Как тебя зовут?")
        return
    new_state = ANKETA_ACTIONS[message.text]
    await state.update_data(is_single_edit=True)
    await state.set_state(new_state)
    check = keyboards.get(new_state, None)
    if check is None:
        await message.answer(prompts.get(new_state, "Не нашли промпт"))
    else:
        await message.answer(prompts.get(new_state, "Не нашли промпт"),
                             reply_markup=check)


@router.message(StateMenu.check_profiles)
async def check_profiles(message: Message, state: FSMContext):
    if not message.text:
        return
    if message.text == "💤":
        await message.answer(f"1.Смотреть Анкеты.\n"
                             "2. Моя анкета.\n"
                             "3.Я больше не хочу никого искать.\n"
                             "4.Активируй Premium - будь в топе\n", reply_markup=zzz_kb)
    if message.text == "Смотреть Анкеты":
        if message.from_user is None:
            return
        profiles = await get_ten(age=25, city='Одесса',
                                looking_for='gender_male', tg_id=message.from_user.id, limit=10)
        if not profiles:
            await message.answer("Анкет не найдено.")
            return
        logger.info(f"profiles {profiles}")
        for p in profiles:
            logger.info(f"{p.id}, {p.media}")
        await message.answer(str(profiles))
        await message.answer(str(profiles[0].name))

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