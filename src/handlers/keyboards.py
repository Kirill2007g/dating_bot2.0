from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

builder = ReplyKeyboardBuilder()

builder.add(KeyboardButton(text="Заполнить анкету"))

builder.adjust(2)

start_markup = builder.as_markup(
    resize_keyboard = True,
    one_time_keyboard = True
)