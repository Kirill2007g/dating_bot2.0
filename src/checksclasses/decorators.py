import inspect
from functools import wraps
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.states import State, StateRegistration, StateMenu
FIELD_ORDER = {"name", "age", "gender",
               "city", "description", "looking_for",
               "media"}
FIELD_ORDER_ = (StateRegistration.name, StateRegistration.age, StateRegistration.gender,
                 StateRegistration.city, StateRegistration.description, StateRegistration.looking_for,
                 StateRegistration.media)
fsm_data_dict = {
    "name": None,
    "age": None,
    "gender": None,
    "city": None,
    "description": None,
    "looking_for": None,
    "media": None,
}

FIELD_PROMPTS = {
    "name": "Как тебя зовут?",
    "age": "Сколько тебе лет?",
    "gender": "Укажи пол",
    "city": "Теперь напиши свой город",
    "description": "Теперь напишите о себе",
    "looking_for": "Кого вы ищете",
    "media": "Пришли фото/видео до 3 штук",
}
dassdf = {
    "name": "Изменить 'Имя'",
    "age": "Изменить 'Возраст'",
    "gender": "Изменить 'Пол'",
    "city": "Изменить 'Город'",
    "description": "Изменить 'О себе'",
    "looking_for": "Изменить 'Кого вы ищете'",
    "media": "Изменить 'Медиа'",
}

button_to_key = {v: k for k, v in dassdf.items()}


_messages: dict[int, list[int]] = {}
from src.states import State, StateRegistration, StateMenu
ANKETA_ACTIONS: dict[str, State] = {
    "Заполнить анкету заново": StateRegistration.make_anketa_again,
    "Изменить несколько пунктов": StateMenu.edit_multiple,
    "Изменить 'Имя'": StateRegistration.name,
    "Изменить 'Возраст'": StateRegistration.age,
    "Изменить 'Пол'": StateRegistration.gender,
    "Изменить 'Город'": StateRegistration.city,
    "Изменить 'О себе'": StateRegistration.description,
    "Изменить 'Кого вы ищете'": StateRegistration.looking_for,
    "Изменить 'Медиа'": StateRegistration.media,
}
prompts = {
        StateRegistration.name: "Как тебя зовут?",
        StateRegistration.age: "Сколько тебе лет?",
        StateRegistration.gender: "Укажи пол",
        StateRegistration.city: "В каком ты городе?",
        StateRegistration.description: "Расскажи о себе",
        StateRegistration.looking_for: "Кого ты ищешь?",
        StateRegistration.media: "Пришли фото или видео",
        StateRegistration.make_anketa_again: "Как тебя зовут?",
        StateMenu.edit_multiple: "Вам дан выбор из пунктов которые вы можете изменить" \
    ", отправляйте в чат по 1 пункту, а когда закончите нажмите на 'ВСЕ!'",
    }
def map_sentences_to_states(sentences: list[str], actions: dict = ANKETA_ACTIONS):
    sentences_copy = sentences.copy()
    if 'ВСЕ!' in sentences_copy:
        sentences_copy.remove('ВСЕ!')
    states = [actions.get(sentence, sentence) for sentence in sentences_copy]
    states.sort(key=lambda state: FIELD_ORDER_.index(state) if state in FIELD_ORDER_ else 0)
    return states
def edit_multiple__(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        sentences_list = next(
            (arg for arg in args if isinstance(arg, list) and all(isinstance(x, str) for x in arg)),
            None
        )
        if sentences_list:
            ready_lst = map_sentences_to_states(sentences_list)
            kwargs["ready_lst"] = ready_lst
        return await func(*args, **kwargs)
    return wrapper
def edit_multiple_y(func):
    @wraps(func)
    async def wrapper(states: list[State], *args, **kwargs):
        if not states:
            return await func(*args, **kwargs)
        else:
            current_state = next((state for state in states if isinstance(state, State)), None)
            current_reply = prompts.get(current_state, "Не нашли соответствующее состояние")


def collect_selection(func):
    @wraps(func)
    async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
        print(f"DEBUG raw={message.text!r} equals_vse={message.text == 'ВСЕ!'}")
        data = await state.get_data()
        selected = list(data.get("selected_fields", []))
        if message.text == 'ВСЕ!':
            kwargs["selected_fields"] = selected
            kwargs["finished"] = True
            kwargs["selected_fields"].append('ВСЕ!')
        else:
            if message.text in button_to_key and message.text not in selected:
                selected.append(message.text)
                await state.update_data(selected_fields=selected)
            kwargs["selected_fields"] = selected
            kwargs['finished'] = False
        return await func(message, state, *args, **kwargs)
    return wrapper

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
    print(f"Deleted messages for chat {chat_id}: {ids}")


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