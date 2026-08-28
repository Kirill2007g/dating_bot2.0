import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo, Message, ReplyKeyboardRemove
from src.db.models import User
from src.db.database import async_sessionmaker
from src.db.db_queries import save_user_in_db

from src.checksclasses.validation import (
    AlbumMiddleware,
    IsValidAge,
    IsValidCity,
    IsValidDescription,
    IsValidGender,
    IsValidLookingfor,
    IsValidName,
)
from src.handlers.keyboards import (
    choose_gender,
    choose_looking_for,
    confirm_kb,
    start_markup,
    menu_kb
)
from src.states import StateRegistration, StateMenu

router = Router()

router.message.middleware(AlbumMiddleware())

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет я бот для поиска пары!\n", reply_markup=start_markup)
    await state.set_state()


@router.message(F.text == "Заполнить анкету")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(StateRegistration.name)
    await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())


@router.message(StateRegistration.name)
async def reg_name(message: Message, state: FSMContext):
    if not await IsValidName()(message):
        return await message.answer("Введи имя")
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(name=message.text)
    await state.set_state(StateRegistration.age)
    await message.answer("Сколько тебе лет")

@router.message(StateRegistration.age)
async def reg_age(message: Message, state: FSMContext):
    if not await IsValidAge()(message):
        return await message.answer("Введи возраст ")
    await state.update_data(age=int(message.text))
    await state.set_state(StateRegistration.gender)
    await message.answer("Теперь выберем пол", reply_markup=choose_gender)

@router.message(StateRegistration.gender)
async def reg_gender(message: Message, state: FSMContext):
    if not await IsValidGender()(message):
        return await message.answer("Выбери пол", reply_markup=choose_gender)
    await state.update_data(gender=message.text)
    await state.set_state(StateRegistration.city)
    await message.answer("Теперь напиши свой город", reply_markup=ReplyKeyboardRemove())


#Доделать
@router.message(StateRegistration.city)
async def reg_city(message: Message, state: FSMContext):
    if not await IsValidCity()(message):
        return await message.answer("Введите название города")
    await state.update_data(city=message.text)
    await state.set_state(StateRegistration.description)
    await message.answer("Теперь напишите о себе")

@router.message(StateRegistration.description)
async def reg_description(message: Message, state: FSMContext):
    # if not await IsValidDescription()(message):
    #     return await message.answer("Напишите о себе")
    await state.update_data(description=message.text)
    await state.set_state(StateRegistration.looking_for)
    await message.answer("Кого вы ищете", reply_markup=choose_looking_for)

@router.message(StateRegistration.looking_for)
async def reg_looking_for(message: Message, state: FSMContext):
    if not await IsValidLookingfor()(message):
        return await message.answer("Кого вы ищете", reply_markup=choose_looking_for)
    await state.update_data(looking_for=message.text)
    await state.set_state(StateRegistration.photo)
    await message.answer("Теперь пришлите фото/видео до 3 штук")

@router.message(StateRegistration.photo, flags={"album": True})
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
async def reg_confirm(message: Message, state: FSMContext):
    if message.text == "Да":
        await message.answer("Отлично анкета сохранена!", reply_markup=menu_kb)
        await state.set_state(StateMenu.menu)




















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










