from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

builder = ReplyKeyboardBuilder()

builder.add(KeyboardButton(text="Заполнить анкету"))

builder.adjust(2)

start_markup = builder.as_markup(
    resize_keyboard = True,
    one_time_keyboard = True
)

builder_2 = ReplyKeyboardBuilder()
builder_2.add(KeyboardButton(text="Я Парень"))
builder_2.add(KeyboardButton(text="Я Девушка"))

builder_2.adjust(2)

choose_gender = builder_2.as_markup(
    resize_keyboard = True,
    one_time_keyboard = True
)