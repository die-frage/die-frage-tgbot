import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from core.states.RegistrationState import RegistrationState
from core.states.AnonymousSurveyState import AnonymousSurveyState
from core.states.AuthorisedSurveyState import SurveyState

from core.handlers.callback import callback
from core.handlers.registration_handlers import handler_start, process_code, process_name, process_mail, process_group
from core.handlers.survey_handlers import handler_of_start_survey, handler_of_anonymous_with_no_choice_answer, handler_of_authenticated_with_no_choice_answer
from core.settings import settings
from core.utils.commands import set_commands


async def init(bot: Bot):
    await set_commands(bot)


async def start():
    bot = Bot(settings.bot.bot_token, parse_mode='HTML')
    dp = Dispatcher()

    dp.startup.register(init)
    dp.message.register(handler_start, Command(commands=['start']))
    dp.message.register(handler_of_start_survey, Command(commands=['survey']))
    dp.message.register(handler_of_start_survey, AnonymousSurveyState.WAITING, SurveyState.WAITING)

    dp.callback_query.register(callback)

    dp.message.register(process_code, RegistrationState.GET_CODE)
    dp.message.register(process_name, RegistrationState.GET_NAME)
    dp.message.register(process_mail, RegistrationState.GET_MAIL)
    dp.message.register(process_group, RegistrationState.GET_GROUP)

    dp.message.register(handler_of_anonymous_with_no_choice_answer, AnonymousSurveyState.TEXT_ANSWER_WAITING)
    dp.message.register(handler_of_authenticated_with_no_choice_answer, SurveyState.TEXT_ANSWER_WAITING)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
