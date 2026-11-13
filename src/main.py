from src.handlers import menu, edit_anketa, registration, check_profiles, settings_
from src.config import settings
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from typing import Optional
from aiogram.fsm.state import State

bot = Bot(token=settings.bot_token.get_secret_value())
dp = Dispatcher(memory=MemoryStorage())

dp.include_router(registration.router)
dp.include_router(menu.router)
dp.include_router(edit_anketa.router_media)
dp.include_router(edit_anketa.router)
dp.include_router(check_profiles.router)
dp.include_router(settings_.router)


async def custom_switch(
        self,
        event: Message | CallbackQuery,
        next_state: State,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup | ReplyKeyboardMarkup] = None,
        **data
        ):
    
    if data:
        await self.update_data(**data)

    await self.set_state(next_state)
    target = event if isinstance(event, Message) else event.message
    if target:
        await target.answer(text, reply_markup=reply_markup)
    if isinstance(event, CallbackQuery):
        await event.answer()

FSMContext.switch = custom_switch

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())