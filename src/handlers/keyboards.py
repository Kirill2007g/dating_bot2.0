from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_keyboard(
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

start_markup = make_keyboard(["Заполнить анкету"], adjust=2)

choose_gender = make_keyboard(["Я Парень", "Я Девушка"], adjust=2)

choose_looking_for = make_keyboard(["Парни", "Девушки", "Без разницы"], adjust=3)

confirm_kb = make_keyboard(["Да", "Нет"], adjust=2)

menu_kb = make_keyboard(
    ["Смотреть анкеты", "Мой профиль", "Настройки", "Заполнить анкету заново"],
    adjust=(4, 1),
    one_time=True,
)

check_profiles = make_keyboard(
    ["❤️", "👎", "💌", "💤"], adjust=(4, 1)
)