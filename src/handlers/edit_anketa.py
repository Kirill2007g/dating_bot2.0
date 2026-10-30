from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.states import StateRegistration, StateMenu
from src.checksclasses.dictionaries import ANKETA_ACTIONS, keyboards, prompts, STATE_TO_FIELD
from src.checksclasses.validation import UserIdMiddleware, AlbumMiddleware, is_valid_description
from src.db.db_queries import update_value, update_media
from src.keyboards import menu_kb
router = Router()
router_media = Router()

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
        await state.set_state(StateMenu.edit_media)
        await message.answer("Отправь фото или видео до 3х штук")
        return
    elif message.text == "Изменить 'О себе'":
        await state.set_state(StateMenu.edit_description)
        await message.answer("Отправьте новое описание о себе")
        return
    state_ = ANKETA_ACTIONS[message.text]
    await message.answer(prompts.get(state_, "Не нашли промпт"))
    if message.from_user is None:
        return
    await state.update_data(tg_id=message.from_user.id, new_state=state_)
    await state.set_state(StateMenu.edit_anketa)
    keyboard_ = keyboards.get(state_, None)
    if keyboard_ is not None:
         await message.answer(prompts.get(state_, "Не нашли промпт"), reply_markup=keyboard_)

@router.message(StateMenu.edit_anketa)
async def edit_anketa(message: Message, callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_state = data.get("new_state")
    if new_state is None or message.from_user is None:
        return
    new_field = STATE_TO_FIELD[new_state]
    value = message.text if message.text is not None else callback_query.message
    await update_value(tg_id=message.from_user.id, field=new_field, value=value)
    await message.answer("Успешно обновили значение", reply_markup=menu_kb)
    await state.set_state(StateMenu.menu)

@router_media.message(StateMenu.edit_media, F.photo | F.video | F.video_note)
async def edit_media(message: Message, state: FSMContext, user_media):
    if user_media is None or message.from_user is None:
        return
    await update_media(tg_id=message.from_user.id, media_list=user_media)
    await message.answer("Успешно обновили значение", reply_markup=menu_kb)
    await state.set_state(StateMenu.menu)

@router.message(StateMenu.edit_description)
async def edit_description(message: Message, state: FSMContext):
    value = await is_valid_description(message)
    await update_value(tg_id=message.from_user.id, field="description", value=value)
    await message.answer("Успешно обновили значение", reply_markup=menu_kb)
    await state.set_state(StateMenu.menu)
