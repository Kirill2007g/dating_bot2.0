from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from src.validation.validation import (
    UserIdMiddleware,
    build_media_group,
    media_list,
    LoggingMiddleware
)
from src.db.db_queries import (
    add_to_seen_ids_table,
    get_all_seen_ids,
    get_profiles_limit,
    UserQueries,
)
from src.keyboards import (
    anketa_kb,
    check_profiles_kb,
    menu_kb,
    settings_kb,
    settings_kb_language,
    settings_kb_premium,
    zzz_kb,
)
from src.states import StateMenu
from src.utils import get_ten_profiles, get_next_profile
router = Router()

router.message.middleware(UserIdMiddleware())
router.message.middleware(LoggingMiddleware())


@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext, tg_user_id: int):
    if not message.text:
        return


    if message.text == "Смотреть анкеты":


        await state.set_state(StateMenu.check_profiles)
        ten_users, profiles = await get_ten_profiles(tg_id=tg_user_id)
        if not profiles:
            return


        user = profiles[0]
        user_media = user.media if hasattr(user, 'media') else None
        if user_media:
            media_list_ = await media_list(user_media)
            media_group = build_media_group(media_list_)
            if media_group:
                await message.answer_media_group(media_group)
                await message.answer(f"{user.name}, {user.age}, {user.city}\n{user.description}", reply_markup=check_profiles_kb)
                ten_users.pop(0)
        user_id = await UserQueries.get_user_id(tg_id=tg_user_id)
        await state.update_data(ten_users_list=ten_users, from_user_id=user_id, to_user_id=user.id, tg_id=tg_user_id)
        await add_to_seen_ids_table(user_tg_id=tg_user_id, viewed_profile_id=user.id)
        await state.set_state(StateMenu.check_profiles)
        return






    if message.text == "Мой профиль":
        if message.from_user is None:
            return
        profile_text = await UserQueries.get_show_form(tg_user_id)
        profile_media = await UserQueries.get_profile_media(tg_user_id)
        if profile_media:
            _media_list = await media_list(profile_media)
            media_group = build_media_group(_media_list)
            if media_group:
                await message.answer_media_group(media_group)
        if profile_text is not None:
            name, age, city, description = profile_text
            await message.answer(f"{name}, {age}, {city}\n{description}", reply_markup=menu_kb)

    if message.text == "Настройки":
        await state.set_state(StateMenu.settings)
        await message.answer("Settings", reply_markup=settings_kb)

    if message.text == "Заполнить анкету заново":
        await message.answer("Выберите одно из:", reply_markup=anketa_kb)
        await state.set_state(StateMenu.anketa)




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

