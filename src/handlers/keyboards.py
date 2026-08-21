from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

builder = ReplyKeyboardBuilder()

builder.add(KeyboardButton(text="Заполнить анкету"))

builder.adjust(2)

start_markup = builder.as_markup(
    resize_keyboard = True,
    one_time_keyboard = False
)

builder_2 = ReplyKeyboardBuilder()
builder_2.add(KeyboardButton(text="Я Парень"))
builder_2.add(KeyboardButton(text="Я Девушка"))

builder_2.adjust(2)

choose_gender = builder_2.as_markup(
    resize_keyboard = True,
    one_time_keyboard = False
)
builder_3 = ReplyKeyboardBuilder()
builder_3.add(KeyboardButton(text="Парни"))
builder_3.add(KeyboardButton(text="Девушки"))
builder_3.add(KeyboardButton(text="Все разницы"))

builder_3.adjust(3)

choose_looking_for = builder_3.as_markup(
    resize_keyboard = True,
    one_time_keyboard = False
)

builder_4 = ReplyKeyboardBuilder()
builder_4.add(KeyboardButton(text="Да"))
builder_4.add(KeyboardButton(text="Нет"))
builder_4.adjust(2)
confirm_kb = builder_4.as_markup(
    resize_keyboard= True,
    one_time_keyboard = False
)

# cancel_builder = ReplyKeyboardBuilder()
# cancel_builder.add(KeyboardButton(text=""))

