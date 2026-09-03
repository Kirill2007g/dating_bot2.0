
from functools import wraps
from aiogram.types import Message

_messages: dict[int, list[int]] = {} # {5, [1]}
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

async def ask(message, text, **kwargs):
    sent = await message.answer(text, **kwargs)
    _messages.setdefault(message.chat.id, []).append(sent.message_id)
    return sent

async def clear(chat_id, bot):
    ids = _messages.get(chat_id, [])
    if not ids:
        return
    try:
        await bot.delete_messages(chat_id=chat_id, message_ids=ids)
    except Exception as e:
        print(f"Error deleting messages for chat {chat_id}: {e}")
    _messages[chat_id] = []



def track_message(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        message = next((arg for arg in args if isinstance(arg, Message)), None)
        album = next((arg for arg in args if isinstance(arg, list) and arg and isinstance(arg, Message)), None)

        if message:
            track(message)
        elif album:
            track(album)


        result = await func(*args, **kwargs)


        if result:
            if isinstance(result, list):
                for item in result:
                    track(item)
            else:
                track(result)

        return result
    return wrapper