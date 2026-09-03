from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def make_keyboard_repr(
        buttons: list[str],
        adjust: int | tuple[int, ...] = 1,
        one_time: bool = False,

) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for text in buttons:
        builder.add(KeyboardButton(text=text))
    if isinstance(adjust, int):
        builder.adjust(adjust)
    else:
        builder.adjust(*adjust)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=one_time)

def make_keyboard_inline(
        buttons: list[str],
        callback_data: list[str] | None = None,
        adjust: int | tuple[int, ...] = 1,
        one_time: bool = False,

) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, text in enumerate(buttons):
        if callback_data:
            builder.add(InlineKeyboardButton(text=text, callback_data=callback_data[i]))
        else:
            builder.add(InlineKeyboardButton(text=text, callback_data=None))
    if isinstance(adjust, int):
        builder.adjust(adjust)
    else:
        builder.adjust(*adjust)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=one_time)

start_markup = make_keyboard_repr(["Заполнить анкету"], adjust=2)

choose_gender = make_keyboard_inline(["Я Парень", "Я Девушка"], adjust=2, callback_data=["gender_male", "gender_female"])

choose_looking_for = make_keyboard_inline(["Парни", "Девушки", "Без разницы"], adjust=3, callback_data=["looking_for_men", "looking_for_women", "looking_for_any"])

confirm_kb = make_keyboard_repr(["Да", "Нет"], adjust=2)

menu_kb = make_keyboard_repr(
    ["Смотреть анкеты", "Мой профиль", "Настройки", "Заполнить анкету заново"],
    adjust=(4, 1),
    one_time=True,
)

check_profiles = make_keyboard_repr (
    ["❤️", "👎", "💌", "💤"], adjust=(4, 1)
)
settings_kb = make_keyboard_repr(
    ["Изменить язык", "Премиум", "Написать в поддержку"], adjust=(4, 4)
)
anketa_kb = make_keyboard_repr(
    ["Заполнить анкету заново", "Изменить несколько пунктов",
      "Изменить 'Имя'", "Изменить 'Возраст'",
        "Изменить 'Пол'", "Изменить 'Город'",
          "Изменить 'О себе'", "Изменить 'Кого вы ищете'",
            "Изменить 'Медиа'"], adjust=(2, 1, 1, 1, 1, 1, 1, 1)
)


