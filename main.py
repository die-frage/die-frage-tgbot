import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

async def main() -> None:
    """Entry point"""
    load_dotenv(".env")
    token = os.getenv("TOKEN_API")
    bot = Bot(token)
    dp = Dispatcher(bot)
    try:
        await dp.start_polling()
    except Exception as _ex:
        print("There is an exception")

if __name__ == "__main__":
    asyncio.run(main)
