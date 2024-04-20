import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram import F

from core.filters.RegistrationState import RegistrationState
from core.filters.SurveyAuthorised import SurveyAuthorised
from core.filters.SurveyAnonymous import SurveyAnonymous

from core.handlers.callback import registration
from core.handlers.registration import get_start, process_code, process_name, process_mail, process_group
from core.handlers.waiting_survey import waiting_start_survey, answer_anonym_text_answer, answer_auth_text_answer
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

    dp.message.register(waiting_start_survey, Command(commands=['survey']))
    dp.message.register(waiting_start_survey, SurveyAnonymous.WAITING)
    dp.message.register(answer_anonym_text_answer, SurveyAnonymous.TEXT_ANSWER_WAITING)
    dp.message.register(answer_auth_text_answer, SurveyAuthorised.TEXT_ANSWER_WAITING)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
