import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers.user_handler import register_user_handlers
from bot.handlers.admin_handler import register_admin_handlers

def register_handler(dp: Dispatcher) -> None:
    register_user_handlers(dp)
    register_admin_handlers(dp)


async def main() -> None:
    """Entry point"""
    load_dotenv(".env")
    token = os.getenv("TOKEN")
    bot = Bot(token)
    dp = Dispatcher()

    register_handler(dp)

    try:
        await dp.start_polling(bot)
    except Exception as _ex:
        print("There is an exception")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
