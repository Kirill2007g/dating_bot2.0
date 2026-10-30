from src.handlers import menu, edit_anketa, registration
from src.config import settings
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=settings.bot_token.get_secret_value())
dp = Dispatcher(memory=MemoryStorage())

dp.include_router(registration.router)
dp.include_router(menu.router)
dp.include_router(edit_anketa.router_media)
dp.include_router(edit_anketa.router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())