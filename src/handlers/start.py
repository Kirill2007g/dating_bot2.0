import asyncio
import json

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, Message, ReplyKeyboardRemove
from sqlalchemy import func
from src.checksclasses.dictionaries import asad, prompts, keyboards
from src.checksclasses.decorators import (ask, clear, track, track_message,
                                        if_one_selected, if_multiple_selected)
from src.checksclasses.validation import (
    AlbumMiddleware,
    IsValidAge,
    IsValidCity,
    IsValidDescription,
    IsValidGender,
    IsValidLookingfor,
    IsValidName,
    LoggingMiddleware,
    build_media_group,
)
from src.db.database import async_sessionmaker
from src.db.db_queries import get_profile, save_user_in_db, get_profile_media, get_profile_text, update_user
from src.db.models import User
from src.handlers.keyboards import (
    choose_gender,
    choose_looking_for,
    confirm_kb,
    menu_kb,
    start_markup,
    anketa_kb,
    check_profiles
)
from src.states import StateMenu, StateRegistration

router = Router()

router.message.middleware(AlbumMiddleware())
router.message.middleware(LoggingMiddleware())
from functools import wraps


WEB_APP_URL =  "https://boondocks-dispersed-stir.ngrok-free.dev"



@router.message(CommandStart())
@track_message
async def command_start_handler(message: Message, state: FSMContext):
    user = message.from_user
    if user is None:
        return
    user_id = user.id
    profile = await get_profile(user_id)
    if profile:
        profile = await get_profile_text(tg_id=user_id)
        profile_media = await get_profile_media(tg_id=user_id)
        media_list = [
            {"type": m.media_type.value, "file_id": m.file_id}
            for m in profile_media
        ]
        media = build_media_group(media_list)
        if media:
            sent_msgs = []
            sent_msgs.append(await message.answer("Так выглядит твоя анкета!"))
            media_messages = await message.answer_media_group(media=media)
            sent_msgs.extend(media_messages)
            sent_msgs.append(await message.answer(profile or "Анкета пока недоступна.", reply_markup=menu_kb))
            await state.set_state(StateMenu.menu)
            return sent_msgs
    await state.clear()
    sent_msg = await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)
    await state.set_state(StateRegistration.name)
    return sent_msg


@router.message(Command("Back"), F.text == "Назад")
async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("/start")
        return
    data = await state.get_data()
    if data.get('is_single_edit', False):
        await state.set_state(StateMenu.anketa)
        return
    else:
        past_state = asad[next(state for state in asad if state.state == current_state)]
        await state.set_state(past_state)
        prompt = prompts.get(past_state, 'Не нашли промпт')
        keyboard = keyboards.get(past_state, 'Не нашли клавиатуру')
        if not prompt:
            await message.answer('Не нашли промпт')
            return
        if prompt and not keyboard:
            await message.answer(prompt)
            return
        if prompt and not keyboard:
            await message.answer(prompt, reply_markup=keyboard)
            return

    await state.clear()
    await message.answer("canceled", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StateMenu.menu)

@router.message(F.text == "Заполнить анкету")
@track_message
async def start_registration(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(StateRegistration.name)
    await clear(message.chat.id, bot)
    bot_msg = await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    return bot_msg

@router.message(StateRegistration.name)
@track_message
@if_one_selected
async def reg_name(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidName()(message):
        return await message.answer("Введи имя")
    await clear(message.chat.id, bot)
    user = message.from_user
    if user is None:
        return
    await state.update_data(tg_id=user.id, name=message.text)
    data = await state.get_data()
    if data.get("is_single_edit", False):
        return True
    await state.set_state(StateRegistration.age)
    return await ask(message, "Сколько тебе лет?")

@router.message(StateRegistration.age)
@track_message
@if_one_selected
async def reg_age(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidAge()(message):
        return await message.answer("Введи возраст ")
    age_text = message.text
    if age_text is None:
        return await message.answer("Введи возраст ")
    await clear(message.chat.id, bot)
    user = message.from_user
    if user is None:
        return
    await state.update_data(tg_id=user.id, age=int(age_text))
    data = await state.get_data()
    if data.get("is_single_edit", False):
        return True
    await state.set_state(StateRegistration.gender)
    bot_msg = await ask(message, "Теперь выберем пол", reply_markup=choose_gender)
    return bot_msg

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
    await state.update_data(tg_id=callback_query.from_user.id, gender=callback_query.data)
    data = await state.get_data()
    is_single_edit = data.get("is_single_edit", False)
    if is_single_edit:
        db_success = await update_user(data)
        if db_success:
            print("База данных успешно обновлена")
        else:
            print("База данных не обновлена")
        await state.update_data(is_single_edit=False)
        await state.set_state(StateMenu.anketa)
        await message.answer("Вы успешно изменили Пол", reply_markup=anketa_kb)
        return

    await state.set_state(StateRegistration.city)
    bot_msg = await ask(message, "Теперь напиши свой город", reply_markup=ReplyKeyboardRemove())
    return bot_msg

#Доделать
@router.message(StateRegistration.city)
@track_message
@if_one_selected
async def reg_city(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidCity()(message):
        return await message.answer("Введите название города")
    user = message.from_user
    if user is None:
        return
    await clear(message.chat.id, bot)
    await state.update_data(tg_id=user.id, city=message.text)
    data = await state.get_data()
    if data.get("is_single_edit", False):
        return True
    await state.set_state(StateRegistration.description)
    bot_msg = await ask(message, "Теперь напишите о себе")
    return bot_msg

@router.message(StateRegistration.description)
@track_message
@if_one_selected
async def reg_description(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidDescription()(message):
        return await message.answer("Напишите о себе")
    user = message.from_user
    if user is None:
        return
    await clear(message.chat.id, bot)
    await state.update_data(tg_id=user.id, description=message.text)
    data = await state.get_data()
    if data.get("is_single_edit", False):
        return True
    await state.set_state(StateRegistration.looking_for)
    bot_msg = await ask(message, "Кого вы ищете", reply_markup=choose_looking_for)
    return bot_msg


@router.callback_query(StateRegistration.looking_for, F.data.in_(['looking_for_men', 'looking_for_women', 'looking_for_any']))
@track_message
@if_one_selected
async def reg_looking_for(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    if callback_query.message is None:
        return
    if not await IsValidLookingfor()(callback_query):
        return await callback_query.message.answer("Кого вы ищете", reply_markup=choose_looking_for)
    await clear(callback_query.message.chat.id, bot)
    await state.update_data(tg_id=callback_query.from_user.id, looking_for=callback_query.data)
    data = await state.get_data()
    if data.get("is_single_edit", False):
        db_success = await update_user(data)
        if db_success:
            print("База данных успешно обновлена")
        else:
            print("База данных не обновлена")
        await state.update_data(is_single_edit=False)
        await state.set_state(StateMenu.anketa)
        await callback_query.message.answer("Вы успешно изменили looking_for", reply_markup=anketa_kb)
        return
    await state.set_state(StateRegistration.media)
    bot_msg = await ask(callback_query.message, "Теперь пришлите фото/видео до 3 штук")
    return bot_msg


@router.message(StateRegistration.media, F.photo | F.video | F.video_note)
@track_message
async def reg_media(message: Message, state: FSMContext, bot: Bot, user_media):
    if not user_media or message.from_user is None:
        return
    await clear(message.chat.id, bot)
    await state.update_data(tg_id=message.from_user.id, user_media_list=user_media)
    data = await state.get_data()
    if data.get("is_single_edit", False):
        db_success = await update_user(data, flag_media=True)
        if db_success:
            print("База данных успешно обновлена")
        else:
            print("База данных не обновлена")
            print(data)
        await state.update_data(is_single_edit=False)
        await state.set_state(StateMenu.anketa)
        await message.answer("Вы успешно обновили медиа", reply_markup=anketa_kb)
        return
    profile_media = build_media_group(user_media)
    if profile_media:
        bot_msg = await ask(message, "Вот как выглядит твоя анкета!", reply_markup=ReplyKeyboardRemove())
        bot_msg2 = await message.answer_media_group(profile_media)
        bot_msg2 = await ask(message, f"{data['name']}, {data['age']}, {data['city']}\n{data['description']}")
        bot_msg3 = await ask(message, "Все верно?", reply_markup=confirm_kb)
        await state.set_state(StateRegistration.confirm)
        return [bot_msg, bot_msg2, bot_msg3]


@router.message(StateRegistration.confirm, F.text.in_({"Да", "Нет"}))
@track_message
async def reg_confirm(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text == "Да":
        await clear(message.chat.id, bot)
        success = await save_user_in_db(fsm_data=data)
        await message.answer("Отлично анкета сохранена!", reply_markup=menu_kb)
        await state.set_state(StateMenu.menu)
    else:
        await clear(message.chat.id, bot)
        await message.answer("Выберите какой пункт хотите исправить:\n", reply_markup=anketa_kb)

























