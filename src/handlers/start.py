import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo, Message, ReplyKeyboardRemove
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
)
from src.states import StateMenu, StateRegistration

router = Router()

router.message.middleware(AlbumMiddleware())

from functools import wraps






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

@router.message(StateRegistration.gender)
@track_message
async def reg_gender(message: Message, state: FSMContext, bot: Bot):
    if not await IsValidGender()(message):
        return await message.answer("Выбери пол", reply_markup=choose_gender)
    await clear(message.chat.id, bot)
    await state.update_data(gender=message.text)
    await state.set_state(StateRegistration.city)
    bot_msg = await ask(message, "Теперь напиши свой город", reply_markup=ReplyKeyboardRemove())
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
async def reg_description(message: Message, state: FSMContext):
    # if not await IsValidDescription()(message):
    #     return await message.answer("Напишите о себе")
    await state.update_data(description=message.text)
    await state.set_state(StateRegistration.looking_for)
    await message.answer("Кого вы ищете", reply_markup=choose_looking_for)

@router.message(StateRegistration.looking_for)
@track_message
async def reg_looking_for(message: Message, state: FSMContext):
    if not await IsValidLookingfor()(message):
        return await message.answer("Кого вы ищете", reply_markup=choose_looking_for)
    await state.update_data(looking_for=message.text)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(StateRegistration.photo)
    await message.answer("Теперь пришлите фото/видео до 3 штук")

@router.message(StateRegistration.photo, flags={"album": True})
@track_message
async def reg_media(message: Message, album: list[Message], state: FSMContext):
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
    await state.update_data(user_media_list=saved_media_data)
    data = await state.get_data()
    success = await save_user_in_db(
        fsm_data=data
    )
    await state.set_state(StateRegistration.confirm)
    await message.answer_media_group(media=media_group_list)
    await message.answer(f"{data['name']}, {data['age']}, {data['city']}\n{data['description']}")
    await message.answer("Все верно?", reply_markup=confirm_kb)




@router.message(StateRegistration.confirm)
@track_message
async def reg_confirm(message: Message, state: FSMContext):
    if message.text == "Да":
        await message.answer("Отлично анкета сохранена!", reply_markup=menu_kb)
        await state.set_state(StateMenu.menu)
    if message.text == "Нет":
        await message.answer("Выберите какой пункт хотите исправить:\n"
        "1. Заполнить анкету заново\n"
        "2. Изменить 'Несколько пунктов'\n"
        "3. Изменить 'Имя'\n"
        "4. Изменить 'Возраст'\n"
        "5. Изменить 'Пол'\n"
        "6.Изменить 'Город'\n"
        "7. Изменить 'О себе'\n"
        "8. Изменить 'Кого вы ищете'\n"
        "9. Изменить 'Медиа'\n")




















# @router.message(StateRegistration.name)
# async def process_name(message: Message, state: FSMContext):

#     # Вызываем наш фильтр вручную прямо в условии!
#     if not await IsValidName()(message):
#         # Если фильтр вернул False — даем ошибку и стопаем выполнение
#         return await message.answer("Неверное имя! Только буквы, до 20 символов.")

#     # Если фильтр вернул True — код спокойно идет дальше
#     await state.update_data(name=message.text)
#     await message.answer("Принято! А теперь введи свой возраст числом:")
#     await state.set_state(StateRegistration.age)










