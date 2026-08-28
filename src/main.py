from src.config import settings
from aiogram import Bot, Dispatcher
from src.handlers import start, viewing
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=settings.bot_token.get_secret_value())
dp = Dispatcher(memory=MemoryStorage())

dp.include_router(start.router)
dp.include_router(viewing.router)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())