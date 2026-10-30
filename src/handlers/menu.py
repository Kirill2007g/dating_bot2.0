from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from src.checksclasses.validation import (
    UserIdMiddleware,
    build_media_group,
    media_list,
)
from src.db.db_queries import (
    add_to_seen_ids_table,
    get_all_seen_ids,
    get_profile,
    get_profile_aclt,
    get_profile_media,
    get_show_form,
    get_ten,
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
router = Router()

router.message.middleware(UserIdMiddleware())


@router.message(StateMenu.menu)
async def menu(message: Message, state: FSMContext, user_id: int):
    if not message.text:
        return
    if message.text == "Смотреть анкеты":
        await state.set_state(StateMenu.check_profiles)
        await message.answer("Смотреть анкеты!!!")
        user_profile = await get_profile(tg_id=user_id)
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
        seen_ids = await get_all_seen_ids(user_tg_id=user_id)
        profiles = get_ten(age, city, looking_for, tg_id, seen_ids=seen_ids)
        await message.answer("УСПЕХ GET TEN")
        if not profiles:
            await message.answer("анкет по критериям не нашли")
            return
        ten_users = []
        for user in profiles:
            await add_to_seen_ids_table(user_tg_id=user_id, viewed_profile_id=user.id)
            await state.set_state(StateMenu.check_profiles)

            ten_users.append({'User': {'name': user.name, 'age': user.age, 'city': user.city,
                                            'looking_for': user.looking_for, 'gender': user.gender,
                                            'description': user.description}})
        await state.update_data(ten_users_list=ten_users)
        user_name = ten_users[0].get('User').get('name')
        user_age = ten_users[0].get('User').get('age')
        user_city = ten_users[0].get('User').get('city')
        user_description = ten_users[0].get('User').get('description')
        ten_users.pop(0)
        await message.answer(f"{user_name}, {user_age}, {user_city}\n{user_description}", reply_markup=check_profiles_kb)
        first = profiles[0]
        media_list_ = await media_list(first.media)
        media_group = build_media_group(media_list_)
        if media_group:
            await message.answer_media_group(media_group)
        await message.answer(f"{first.name}, {first.age}, {first.city}\n{first.description}")

    if message.text == "Мой профиль":
        if message.from_user is None:
            return
        profile_text = await get_show_form(user_id)
        profile_media = await get_profile_media(user_id)
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
        # logger.debug(f"словили message")


@router.message(StateMenu.check_profiles)
async def check_profiles(message: Message, state: FSMContext, user_id: int):
    # boolean = True
    # while boolean == True:
    #     if not message.text:
    #         return
    #     data = await state.get_data()
    #     ten_users = data.get("ten_users_list", [])
    #     async def get_aclt_and_show():
    #         user_name = ten_users[0].get('User').get('name')
    #         user_age = ten_users[0].get('User').get('age')
    #         user_city = ten_users[0].get('User').get('city')
    #         user_description = ten_users[0].get('User').get('description')
    #         ten_users.pop(0)
    #         await message.answer(f"{user_name}, {user_age}, {user_city}\n{user_description}", reply_markup=check_profiles_kb)
    if not message.text:
        return
    data = await state.get_data()
    ten_users = data.get("ten_users_list", [])
    async def get_aclt_and_show():
        user_name = ten_users[0].get('User').get('name')
        user_age = ten_users[0].get('User').get('age')
        user_city = ten_users[0].get('User').get('city')
        user_description = ten_users[0].get('User').get('description')
        ten_users.pop(0)
        await message.answer(f"{user_name}, {user_age}, {user_city}\n{user_description}", reply_markup=check_profiles_kb)
        if not ten_users:
            await you()
    async def you():
        user_profile = await get_profile(tg_id=user_id)
        user_aclt = await get_profile_aclt(user_profile.tg_id)
        age, city, looking_for, tg_id = user_aclt
        seen_ids = await get_all_seen_ids(user_tg_id=user_id)
        profiles = get_ten(age, city, looking_for, tg_id, seen_ids=seen_ids)
        ten_users = []
        for user in profiles:
            await add_to_seen_ids_table(user_tg_id=user_id, viewed_profile_id=user.id)
            ten_users.append({'User': {'name': user.name, 'age': user.age, 'city': user.city,
                                                        'looking_for': user.looking_for, 'gender': user.gender,
                                                        'description': user.description}})
        await get_aclt_and_show()
    if message.text == "💤":
        await message.answer("1.Смотреть Анкеты.\n"
                             "2. Моя анкета.\n"
                             "3.Я больше не хочу никого искать.\n"
                             "4.Активируй Premium - будь в топе\n", reply_markup=zzz_kb)

    if message.text == '❤️':
        try:
            await get_aclt_and_show()

        except IndexError as e:
            pass
    if message.text == '👎':
        try:
            await get_aclt_and_show()
        except IndexError as e:
            pass
    if message.text == '💌':
        pass

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

