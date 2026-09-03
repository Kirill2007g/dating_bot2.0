import asyncio
import json

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, Message, ReplyKeyboardRemove, WebAppInfo
from sqlalchemy import func

from src.checksclasses.decorators import ask, clear, track, track_message
from src.checksclasses.validation import (
    AlbumMiddleware,
    IsValidAge,
    IsValidCity,
    IsValidDescription,
    IsValidGender,
    IsValidLookingfor,
    IsValidName,
    build_media_group,
)
from src.db.database import async_sessionmaker
from src.db.db_queries import get_profile, save_user_in_db
from src.db.models import User
from src.handlers.keyboards import (
    choose_gender,
    choose_looking_for,
    confirm_kb,
    menu_kb,
    start_markup,
    anketa_kb,
)
from src.states import StateMenu, StateRegistration

router = Router()

router.message.middleware(AlbumMiddleware())

from functools import wraps


WEB_APP_URL =  "https://boondocks-dispersed-stir.ngrok-free.dev"



@router.message(CommandStart())
@track_message
async def command_start_handler(message: Message, state: FSMContext):
    profile = await get_profile(message.from_user.id, 1)
    if profile:
        profile = await get_profile(tg_id=message.from_user.id, n=3)
        media_list = await get_profile(tg_id=message.from_user.id, n=4)
        if media_list:
            media = build_media_group(media_list)
            sent_msgs = []
            sent_msgs.append(await message.answer("Так выглядит твоя анкета!"))
            media_messages = await message.answer_media_group(media=media)
            sent_msgs.extend(media_messages)
            sent_msgs.append(await message.answer(profile))
            await state.set_state(StateMenu.menu)
            return sent_msgs
    await state.clear()
    sent_msg = await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)
    await state.set_state(StateRegistration.name)
    return sent_msg


@router.message(F.text == "Заполнить анкету")
@track_message
async def start_registration(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(StateRegistration.name)
    await clear(message.chat.id, bot)
    bot_msg = await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    return bot_msg


@router.message(StateRegistration.name)
@track_message
async def reg_name(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidName()(message):
        return await message.answer("Введи имя")
    await clear(message.chat.id, bot)
    await state.update_data(tg_id=message.from_user.id, name=message.text)
    await state.set_state(StateRegistration.age)
    bot_msg = await ask(message, "Сколько тебе лет?")
    return bot_msg



@router.message(StateRegistration.age)
@track_message
async def reg_age(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidAge()(message):
        return await message.answer("Введи возраст ")
    await clear(message.chat.id, bot)
    await state.update_data(age=int(message.text))
    await state.set_state(StateRegistration.gender)
    bot_msg = await ask(message, "Теперь выберем пол", reply_markup=choose_gender)
    return bot_msg

@router.callback_query(StateRegistration.gender, F.data.in_(['gender_male', 'gender_female']))
@track_message
async def reg_gender(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    if not await IsValidGender()(callback_query):
        return await callback_query.message.answer("Выбери пол", reply_markup=choose_gender)
    await clear(callback_query.message.chat.id, bot)
    await state.update_data(gender=callback_query.data)
    await state.set_state(StateRegistration.city)
    bot_msg = await ask(callback_query.message, "Теперь напиши свой город", reply_markup=ReplyKeyboardRemove())
    return bot_msg



#Доделать
@router.message(StateRegistration.city)
@track_message
async def reg_city(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidCity()(message):
        return await message.answer("Введите название города")
    await clear(message.chat.id, bot)
    await state.update_data(city=message.text)
    await state.set_state(StateRegistration.description)
    bot_msg = await ask(message, "Теперь напишите о себе")
    return bot_msg

@router.message(StateRegistration.description)
@track_message
async def reg_description(message: Message, state: FSMContext, bot: Bot):
    # if not await IsValidDescription()(message):
    #     return await message.answer("Напишите о себе")
    await clear(message.chat.id, bot)
    await state.update_data(description=message.text)
    await state.set_state(StateRegistration.looking_for)
    bot_msg = await ask(message, "Кого вы ищете", reply_markup=choose_looking_for)
    return bot_msg


@router.callback_query(StateRegistration.looking_for, F.data.in_(['looking_for_men', 'looking_for_women', 'looking_for_any']))
@track_message
async def reg_looking_for(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    if not await IsValidLookingfor()(callback_query):
        return await callback_query.message.answer("Кого вы ищете", reply_markup=choose_looking_for)
    await clear(callback_query.message.chat.id, bot)
    await state.update_data(looking_for=callback_query.data)
    await state.set_state(StateRegistration.photo)
    bot_msg = await ask(callback_query.message, "Теперь пришлите фото/видео до 3 штук")
    return bot_msg


@router.message(StateRegistration.photo, flags={"album": True})
@track_message
async def reg_media(message: Message, album: list[Message], state: FSMContext, bot: Bot):
    await clear(message.chat.id, bot)
    media_group_list = []
    saved_media_data = []
    for m in album:
        if m.photo:
            file_id = m.photo[-1].file_id
            media_group_list.append(InputMediaPhoto(media=file_id))
            saved_media_data.append({"type": "photo", "file_id": file_id})
        elif m.video:
            file_id = m.video.file_id
            media_group_list.append(InputMediaVideo(media=file_id))
            saved_media_data.append({"type": "video", "file_id": file_id})
        elif m.video_note:
            file_id = m.video_note.file_id
            saved_media_data.append({"type": "video_note", "file_id": file_id})

            await m.answer_video_note(video_note=file_id)
    if media_group_list:
        first = media_group_list[0]
        if isinstance(first, InputMediaPhoto):
            media_group_list[0] = InputMediaPhoto(
                media=first.media
            )
        elif isinstance(first, InputMediaVideo):
            media_group_list[0] = InputMediaVideo(media=first.media)
    data = await state.get_data()
    await state.update_data(user_media_list=saved_media_data)
    bot_msg = await ask(message, "Вот как выглядит твоя анкета!", reply_markup=ReplyKeyboardRemove())
    bot_msg2 = await ask(message, f"{data['name']}, {data['age']}, {data['city']}\n{data['description']}")
    bot_msg3 = await ask(message, "Все верно?", reply_markup=confirm_kb)
    if message.text == "Да":
        success = await save_user_in_db(fsm_data=data)
        await message.answer("Отлично анкета сохранена!", reply_markup=menu_kb)
        await state.set_state(StateMenu.menu)
    if message.text == "Нет":
        await message.answer("Выберите какой пункт хотите исправить:\n", reply_markup=anketa_kb)
    return [bot_msg, bot_msg2, bot_msg3]

# @router.message(StateRegistration.make_anketa_again)
# @track_message
# async def make_anketa_again(message: Message, state: FSMContext, bot: Bot





@router.message(Command("webapp"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⚙️ Открыть настройки",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ])
    await message.answer("Нажми на кнопку ниже, чтобы открыть Mini App:", reply_markup=keyboard)


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    data = json.loads(message.web_app_data.data)
    if "gender" in data or "looking_for" in data:
        await message.answer("mini apps СРАБОТАЛ")
























