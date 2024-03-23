from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Пройти опрос'
        ),
        BotCommand(
            command='info',
            description='Получить информацию'
        ),
        BotCommand(
            command='prof',
            description='Для организаторов'
        )
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
