from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from src.checksclasses.decorators import ask, clear, track_message
from src.checksclasses.dictionaries import keyboards, prompts, saps, INVALID_TEXT
from src.validation.validation import (
    AlbumMiddleware,
    IsValidAge,
    IsValidCity,
    is_valid_description,
    IsValidGender,
    IsValidLookingfor,
    IsValidName,
    UserIdMiddleware,
    IsSingleEdit,
    build_media_group,
    media_list,
    LoggingMiddleware
)
from src.db.db_queries import (
    UserQueries,
    add_user_id_to_redis,
    check_user_id_in_redis
)

from src.keyboards import (
    anketa_kb,
    choose_gender,
    choose_looking_for,
    confirm_kb,
    menu_kb,
    start_markup,
)
from src.states import StateMenu, StateRegistration, StateEdit

router = Router()

router.message.middleware(AlbumMiddleware())
router.message.middleware(UserIdMiddleware())
router.message.middleware(LoggingMiddleware())



@router.message(CommandStart())
@track_message
async def command_start_handler(message: Message, state: FSMContext, tg_user_id: int):
    await message.answer("⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️")
    await add_user_id_to_redis(tg_user_id)
    profile = await UserQueries.get_profile(tg_user_id)
    if profile:
        profile = await UserQueries.get_show_form(tg_id=tg_user_id)
        profile_media = await UserQueries.get_profile_media(tg_id=tg_user_id)
        media_list_ = await media_list(profile_media)
        media = build_media_group(media_list_)
        if media:
            sent_msgs = []
            sent_msgs.append(await message.answer("Так выглядит твоя анкета!"))
            media_messages = await message.answer_media_group(media=media)
            sent_msgs.extend(media_messages)
            if profile is not None:
                name, age, city, description = profile
                profile_text = f"{name}, {age}, {city}\n{description}"
                sent_msgs.append(await message.answer(str(profile_text) if profile else "Анкета пока недоступна.", reply_markup=menu_kb))
            await state.set_state(StateMenu.menu)
            return sent_msgs
    await state.clear()
    sent_msg = await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)
    await state.set_state(StateRegistration.name)
    return sent_msg


# @router.message(F.text == 'Назад')
# async def cancel(message: Message, state: FSMContext, tg_user_id: int):
#     current_state = await state.get_state()
#     if current_state is None:
#         await message.answer("/start")
#         return
#     data = await state.get_data()
#     past_state = saps.get(current_state, 'sa')
#     await state.set_state(past_state)
#     prompt = prompts.get(past_state, 'Не нашли промпт')
#     keyboard = keyboards.get(past_state, 'Не нашли клавиатуру')
#     if not prompt:
#         await message.answer('Не нашли промпт')
#         return
#     if prompt and not keyboard:
#         await message.answer(prompt)
#         return
#     if prompt and keyboard:
#         await message.answer(prompt, reply_markup=keyboard)
#         return

#     await state.clear()
#     await message.answer("canceled", reply_markup=ReplyKeyboardRemove())
#     await state.set_state(StateMenu.menu)

@router.message(F.text == "Заполнить анкету")
@track_message
async def start_registration(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(StateRegistration.name)
    await clear(message.chat.id, bot)
    bot_msg = await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    return bot_msg




@router.message(StateRegistration.name, IsValidName())
@track_message
async def reg_name(message: Message, state: FSMContext, bot: Bot, tg_user_id: int):
    await clear(message.chat.id, bot)
    await state.switch(message, next_state=StateRegistration.age, text="Сколько тебе лет?", tg_id=tg_user_id, name=message.text)


@router.message(StateRegistration.age, IsValidAge())
@track_message
async def reg_age(message: Message, state: FSMContext, bot: Bot, tg_user_id: int):
    age_text = message.text
    if age_text is None:
        return await message.answer("Введи возраст ")
    await clear(message.chat.id, bot)
    await state.switch(message, next_state=StateRegistration.gender, text="Теперь выберем пол", reply_markup=choose_gender, tg_id=tg_user_id, age=int(age_text))


@router.callback_query(StateRegistration.gender, F.data.in_(['gender_male', 'gender_female']))
@track_message
async def reg_gender(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    if not await IsValidGender()(callback_query):
        message = callback_query.message
        if message is None:
            return
        return await message.answer("Выбери пол", reply_markup=choose_gender)
    message = callback_query.message
    if message is None:
        return
    
    await clear(message.chat.id, bot)
    await state.switch(callback_query, next_state=StateRegistration.city, text="Теперь напиши свой город", tg_id=callback_query.from_user.id, gender=callback_query.data, reply_markup=ReplyKeyboardRemove())


@router.message(StateRegistration.gender)
async def gender_wrong_input(message: Message):
    await message.answer("Выбери кнопкой, какой у тебя пол?", reply_markup=choose_gender)


@router.message(StateRegistration.city, IsValidCity())
@track_message
async def reg_city(message: Message, state: FSMContext, bot: Bot, tg_user_id: int):
    await clear(message.chat.id, bot)
    await state.switch(message, next_state=StateRegistration.description, text="Теперь напиши о себе", tg_id=tg_user_id, city=message.text)


@router.message(StateRegistration.description)
@track_message
async def reg_description(message: Message, state: FSMContext, bot: Bot, tg_user_id: int):
    valid_description = await is_valid_description(message)
    if valid_description is False:
        return
    await clear(message.chat.id, bot)
    await state.switch(message, next_state=StateRegistration.looking_for, text="Кого вы ищете", tg_id=tg_user_id, description=message.text, reply_markup=choose_looking_for)



@router.callback_query(StateRegistration.looking_for, F.data.in_(['looking_for_male', 'looking_for_female', 'looking_for_any']))
@track_message
async def reg_looking_for(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    if callback_query.message is None:
        return
    if not await IsValidLookingfor()(callback_query):
        return await callback_query.message.answer("Кого вы ищете", reply_markup=choose_looking_for)
    await clear(callback_query.message.chat.id, bot)
    await state.switch(callback_query, next_state=StateRegistration.media, text="Теперь пришлите фото/видео до 3 штук", tg_id=callback_query.from_user.id, looking_for=callback_query.data)


@router.message(StateRegistration.looking_for)
async def looking_for_wrong_input(message: Message):
    await message.answer("Выбери кнопкой, кого вы ищётё", reply_markup=choose_looking_for)


@router.message(StateRegistration.media, F.photo | F.video | F.video_note)
@track_message
async def reg_media(message: Message, state: FSMContext, bot: Bot, user_media):
    if not user_media or message.from_user is None:
        return
    await clear(message.chat.id, bot)
    await state.update_data(tg_id=message.from_user.id, user_media_list=user_media)
    data = await state.get_data()
    profile_media = build_media_group(user_media)
    if profile_media:
        bot_msg = await ask(message, "Вот как выглядит твоя анкета!", reply_markup=ReplyKeyboardRemove())
        bot_msg1 = await message.answer_media_group(profile_media)
        bot_msg2 = await ask(message, f"{data.get('name')}, {data.get('age')}, {data['city']}\n{data['description']}")
        bot_msg3 = await ask(message, "Все верно?", reply_markup=confirm_kb)
        await state.set_state(StateRegistration.confirm)
        return [bot_msg, bot_msg1, bot_msg2, bot_msg3]

@router.message(StateRegistration.media)
async def media_wrong_input(message: Message):
    await message.answer("Отправьте фото/видео до 3 штук")

@router.message(StateRegistration.confirm, F.text.in_({"Да", "Нет"}))
@track_message
async def reg_confirm(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text == "Да":
        await clear(message.chat.id, bot)
        await UserQueries.save_user_in_db(fsm_data=data)
        await message.answer("Отично анкета сохранена!", reply_markup=menu_kb)
        await message.answer(
        "1. Смотреть анкеты\n" 
        "2. Мой профиль\n" 
        "3. Настройки\n" 
        "4. Заполнить анкету заново\n")
        await state.set_state(StateMenu.menu)
    else:
        await clear(message.chat.id, bot)
        await message.answer("Выберите какой пункт хотите исправить:\n", reply_markup=anketa_kb)
        await state.set_state(StateEdit.edit_anketa)


@router.message(StateFilter(StateRegistration.name, StateRegistration.age,
                            StateRegistration.city, StateRegistration.description))
async def invalid_input(message: Message, state: FSMContext):
    await message.answer(INVALID_TEXT[await state.get_state()])













