from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.states import StateRegistration, StateEdit, StateMenu
from src.checksclasses.dictionaries import ANKETA_ACTIONS, keyboards, prompts, STATE_TO_FIELD
from src.validation.validation import UserIdMiddleware, AlbumMiddleware, is_valid_description, LoggingMiddleware
from src.db.db_queries import UserQueries
from src.keyboards import menu_kb
router = Router()
router_media = Router()
router.message.middleware(LoggingMiddleware())
router.message.middleware(UserIdMiddleware())
router_media.message.middleware(AlbumMiddleware())


@router.message(StateMenu.anketa, F.text.in_(ANKETA_ACTIONS.keys()))
async def handle_actions(message: Message, state: FSMContext):
    if message.text is None:
        return
    if message.text == "Заполнить анкету заново":
        await state.set_state(StateRegistration.name)
        await message.answer("Как тебя зовут?")
        return
    elif message.text == "Изменить 'Медиа'":
        await state.set_state(StateEdit.edit_media)
        await message.answer("Отправь фото или видео до 3х штук")
        return
    elif message.text == "Изменить 'О себе'":
        await state.set_state(StateEdit.edit_description)
        await message.answer("Отправьте новое описание о себе")
        return
    state_ = ANKETA_ACTIONS[message.text]
    await message.answer(prompts.get(state_, "Не нашли промпт"))
    if message.from_user is None:
        return
    await state.update_data(tg_id=message.from_user.id, new_state=state_)
    await state.set_state(StateEdit.edit_anketa)
    keyboard_ = keyboards.get(state_, None)
    if keyboard_ is not None:
         await message.answer(prompts.get(state_, "Не нашли промпт"), reply_markup=keyboard_)

@router.message(StateEdit.edit_anketa)
async def edit_anketa(message: Message, callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_state = data.get("new_state")
    if new_state is None or message.from_user is None:
        return
    new_field = STATE_TO_FIELD[new_state]
    value = message.text if message.text is not None else callback_query.message
    await UserQueries.update_user(data={new_field: value}, flag_media=False)
    await message.answer("Успешно обновили значение", reply_markup=menu_kb)
    await state.set_state(StateMenu.menu)

@router_media.message(StateEdit.edit_media, F.photo | F.video | F.video_note)
async def edit_media(message: Message, state: FSMContext, user_media):
    if user_media is None or message.from_user is None:
        return
    await UserQueries.update_user(data={"media": user_media}, flag_media=True)
    await message.answer("Успешно обновили значение", reply_markup=menu_kb)
    await state.set_state(StateMenu.menu)

@router.message(StateEdit.edit_description)
async def edit_description(message: Message, state: FSMContext):
    value = await is_valid_description(message)
    await UserQueries.update_user(data={"description": value}, flag_media=False)
    await message.answer("Успешно обновили значение", reply_markup=menu_kb)
    await state.set_state(StateMenu.menu)
