from src.states import State, StateMenu, StateRegistration
from src.handlers.keyboards import ( choose_gender, choose_looking_for,
                                    anketa_kb, settings_kb, menu_kb)
_messages: dict[int, list[int]] = {}


FIELD_PROMPTS: dict[str, str] = {
    "name": "Как тебя зовут?",
    "age": "Сколько тебе лет?",
    "gender": "Укажи пол",
    "city": "Теперь напиши свой город",
    "description": "Теперь напишите о себе",
    "looking_for": "Кого вы ищете",
    "media": "Пришли фото/видео до 3 штук",
}
INVALID_TEXT: dict[str | None, str] = {
    StateRegistration.name.state: "Введи имя",
    StateRegistration.age.state: "Введи возраст",
    StateRegistration.city.state: "Введи название города",
    StateRegistration.description.state: "Вы превысили лимит в 1000 символов"

}
ALLOWED_FIELDS: set[str] = {"name", "age", "city", "description", "gender", "looking_for"}
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
prompts: dict[State | None, str] = {
        StateRegistration.name: "Как тебя зовут?",
        StateRegistration.age: "Сколько тебе лет?",
        StateRegistration.gender: "Укажи пол",
        StateRegistration.city: "В каком ты городе?",
        StateRegistration.description: "Расскажи о себе",
        StateRegistration.looking_for: "Кого ты ищешь?",
        StateRegistration.media: "Пришли фото или видео до 3х штук",
        StateRegistration.make_anketa_again: "Как тебя зовут?",
        StateMenu.settings: "Settings",
        StateMenu.anketa: 'state_anketa'
    }
STATE_TO_FIELD: dict[State, str] = {
    StateRegistration.name: "name",
    StateRegistration.age: "age",
    StateRegistration.city: "city",
    StateRegistration.gender: "gender",
    StateRegistration.description: "description",
    StateRegistration.looking_for: "looking_for"
}
#state and past state сокращенно saps
saps: dict[State, State] = {
        StateMenu.anketa: StateMenu.menu,
        StateMenu.settings: StateMenu.menu,
        StateRegistration.media: StateRegistration.looking_for,
        StateRegistration.looking_for: StateRegistration.description,
        StateRegistration.description: StateRegistration.city,
        StateRegistration.city: StateRegistration.gender,
        StateRegistration.gender: StateRegistration.age,
        StateRegistration.age: StateRegistration.name}
keyboards = {
        StateMenu.anketa: anketa_kb,
        StateMenu.settings: settings_kb,
        StateRegistration.gender: choose_gender,
        StateRegistration.looking_for: choose_looking_for,
        StateMenu.menu: menu_kb,
    }

