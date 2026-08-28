from src.config import settings
from aiogram import Bot, Dispatcher
from src.handlers import start
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=settings.bot_token.get_secret_value())
dp = Dispatcher(memory=MemoryStorage())

dp.include_router(start.router)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())