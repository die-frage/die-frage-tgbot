from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Зарегистрироваться'
        ),
        BotCommand(
            command='run',
            description='Начать опрос'
        )
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
