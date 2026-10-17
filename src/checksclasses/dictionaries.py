from src.states import State, StateMenu, StateRegistration
from src.handlers.keyboards import ( choose_gender, choose_looking_for,
                                    anketa_kb, settings_kb, menu_kb)
_messages: dict[int, list[int]] = {}

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


ANKETA_ACTIONS: dict[str, State] = {
    "Заполнить анкету заново": StateRegistration.make_anketa_again,
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
        StateMenu.settings: "Settings",
        StateMenu.anketa: 'state_anketa'
    }
asad = {
        StateMenu.anketa: 'StateMenu.menu',
        StateMenu.settings: StateMenu.menu,
        StateRegistration.media: StateRegistration.looking_for,
        StateRegistration.looking_for: StateRegistration.description,
        StateRegistration.description: StateRegistration.city,
        StateRegistration.city: StateRegistration.gender,
        StateRegistration.gender: StateRegistration.age,
        StateRegistration.age: StateRegistration.name}
cancel_dict = {v: k for k, v in asad.items()}
keyboards = {
        StateMenu.anketa: anketa_kb,
        StateMenu.settings: settings_kb,
        StateRegistration.gender: choose_gender,
        StateRegistration.looking_for: choose_looking_for,
        StateMenu.menu: menu_kb,
    }
button_to_key = {v: k for k, v in dassdf.items()}
anketa_actions_reverse = {v: k for k, v in ANKETA_ACTIONS.items()}
