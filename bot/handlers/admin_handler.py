from aiogram import Bot, Dispatcher
import os

async def start_bot_admin(bot: Bot) -> None:
    admin_id = os.getenv("ADMIN_ID")
    await bot.send_message(admin_id, text="Bot is running")

async def stop_bot_admin(bot: Bot) -> None:
    admin_id = os.getenv("ADMIN_ID")
    await bot.send_message(admin_id, text="Bot has stopped")

def register_admin_handlers(dp: Dispatcher) -> None:
    dp.startup.register(start_bot_admin)
    dp.shutdown.register(stop_bot_admin)
