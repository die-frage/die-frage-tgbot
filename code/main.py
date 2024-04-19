import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from core.filters.RegistrationState import RegistrationState
from core.handlers.callback import registration
from core.handlers.registration import get_start, process_code, process_name, process_mail, process_group
from core.settings import settings
from core.utils.commands import set_commands


async def init(bot: Bot):
    await set_commands(bot)


async def start():
    bot = Bot(settings.bot.bot_token, parse_mode='HTML')
    dp = Dispatcher()

    dp.startup.register(init)
    dp.message.register(get_start, Command(commands=['start']))
    dp.callback_query.register(registration)

    dp.message.register(process_code, RegistrationState.GET_CODE)
    dp.message.register(process_name, RegistrationState.GET_NAME)
    dp.message.register(process_mail, RegistrationState.GET_MAIL)
    dp.message.register(process_group, RegistrationState.GET_GROUP)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
