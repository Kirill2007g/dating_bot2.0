import inspect
from functools import wraps
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states import State, StateMenu, StateRegistration
from src.db.db_queries import update_user
from src.checksclasses.dictionaries import ANKETA_ACTIONS,  prompts, _messages
from src.handlers.keyboards import anketa_kb



# if_one_selected - декоратор для функции которая вызывается если выбран один пункт
def if_one_selected(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        state = kwargs.get("state") or next(
            (arg for arg in args if isinstance(arg, FSMContext)), None
        )
        message = next((arg for arg in args if isinstance(arg, Message)), None)
        result = await func(*args, **kwargs)
        if not result or not state or not message:
            return result
        fsm_data = await state.get_data()
        if not fsm_data.get("is_single_edit", False):
            return result
        db_success = await update_user(data=fsm_data)
        if db_success:
            print("[ДЕКОРАТОР] База данных успешно обновлена!")
        else:
            print("[ДЕКОРАТОР] Ошибка при обновлении базы данных!")
        await state.update_data(is_single_edit=False)
        await state.set_state(StateMenu.anketa)
        return await message.answer("Вы вернулись в меню анкеты.", reply_markup=anketa_kb)
    return wrapper

# Функция для сохранения ID сообщений в глобальном словаре _messages.
# Универсальна: может принимать как одно сообщение (Message), так и список (list[Message]).
# Используется для очистки истории переписки в чате.
def track(message):
    if not message:
        return
    msgs = message if isinstance(message, list) else [message]
    if not msgs:
        return
    chat_id = msgs[0].chat.id
    ids = _messages.setdefault(chat_id, [])
    for m in msgs:
        if m.message_id not in ids:
            ids.append(m.message_id)
    print(f"Tracked messages for chat {chat_id}: {ids}")

# Функция-помощник для отправки текстовых сообщений ботом.
# Автоматически сохраняет ID отправленного ботом сообщения в словарь _messages для последующего удаления.
async def ask(message, text, **kwargs):
    sent = await message.answer(text, **kwargs)
    _messages.setdefault(message.chat.id, []).append(sent.message_id)
    return sent

# Функция для массового удаления всех накопленных сообщений в конкретном чате.
# Удаляет как входящие сообщения пользователя, так и ответы бота, если их ID были сохранены в _messages.
async def clear(chat_id, bot):
    ids = _messages.get(chat_id, [])
    if not ids:
        return
    try:
        await bot.delete_messages(chat_id=chat_id, message_ids=ids)
    except Exception as e:
        print(f"Error deleting messages for chat {chat_id}: {e}")
    _messages[chat_id] = []
    print(f"Deleted messages for chat {chat_id}: {ids}")

# 1. Автоматически логирует (трекает) входящие сообщения/альбомы ОТ ПОЛЬЗОВАТЕЛЯ до выполнения хендлера.
# 2. Передает в хендлер список ранее сохраненных ID сообщений, если в аргументах функции есть 'tracked_messages'.
# 3. Перехватывает возвращенные хендлером сообщения ОТ БОТА (через return) и тоже добавляет их в очередь на удаление.
def track_message(func):
    wants_tracked = "tracked_messages" in inspect.signature(func).parameters
    @wraps(func)
    async def wrapper(*args, **kwargs):
        message = next((arg for arg in args if isinstance(arg, Message)), None)
        album = next((arg for arg in args if isinstance(arg, list) and arg and isinstance(arg[0], Message)), None)
        if message:
            track(message)
        elif album:
            track(album)
        if wants_tracked:
            chat_id = message.chat.id if message else (album[0].chat.id if album else None)
            kwargs["tracked_messages"] = list(_messages.get(chat_id, [])) if chat_id is not None else []
        result = await func(*args, **kwargs)
        if result:
            if isinstance(result, list):
                for item in result:
                    track(item)
            else:
                track(result)
        return result
    return wrapper