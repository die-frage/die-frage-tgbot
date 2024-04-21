import requests
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from core.keybords.inline_keyboards import enter_code_keyboard, finish_registration_keyboard
from datetime import datetime
from core.states.RegistrationState import RegistrationState
from core.states.AnonymousSurveyState import AnonymousSurveyState
from core.states.AuthorisedSurveyState import AuthorisedSurveyState

# Urls
url_get_survey_by_code = 'http://localhost:8787/api/survey/code/'


async def handler_start(message: Message, bot: Bot, state: FSMContext):
    text = message.text.replace("/start", "")
    if len(text) < 1:
        msg = "Это телеграм бот для <b>проведения опросов</b>"
        await bot.send_message(message.from_user.id, msg)
        msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
        await bot.send_message(message.from_user.id, msg)
        msg = "Для прохождения опроса отсканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
              "нажав на кнопку\n "
        await bot.send_message(message.from_user.id, msg, reply_markup=enter_code_keyboard)
    else:
        await process_code(message, bot, state)


async def process_code(message: Message, bot: Bot, state: FSMContext):
    code = message.text.replace("/start ", "")
    url = url_get_survey_by_code + code
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        begin_datetime = datetime.fromisoformat(data['date_begin'][:-6])
        end_datetime = datetime.fromisoformat(data['date_end'][:-6])
        begin_formatted = begin_datetime.strftime('%H:%M %d.%m.%Y')
        end_formatted = end_datetime.strftime('%H:%M %d.%m.%Y')
        await state.update_data(code=code)
        await state.update_data(data_begin=begin_formatted)
        await state.update_data(data_end=end_formatted)
        await state.update_data(title=data['title'])
        await state.update_data(survey_id=data['id'])
        if not data['anonymous']:
            await bot.send_message(message.from_user.id, "Введите <b>ФИО</b> ")
            await state.set_state(RegistrationState.GET_NAME)
        else:
            data = await state.get_data()
            data_begin = data['data_begin']
            data_end = data['data_end']
            title = data['title']
            msg = f'Проверьте данные:\n\n' \
                  f'<b>Опрос: </b>{title}\n' \
                  f'<b>Начало: </b>{data_begin}\n' \
                  f'<b>Конец: </b>{data_end}\n\n'

            await bot.send_message(message.from_user.id, msg)
            msg = "Данные правильные?"
            await bot.send_message(message.from_user.id, msg, reply_markup=finish_registration_keyboard)
            await state.set_state(AnonymousSurveyState.REGISTERED)
    except requests.exceptions.RequestException as e:
        await handle_request_exception(message, bot, state, e)


async def process_name(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(name=message.text)
    await bot.send_message(message.from_user.id, "Введите <b>почту</b> ")
    await state.set_state(RegistrationState.GET_MAIL)


async def process_mail(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(mail=message.text)
    await bot.send_message(message.from_user.id, "Введите <b>номер учебной группы</b> ")
    await state.set_state(RegistrationState.GET_GROUP)


async def process_group(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(group=message.text)

    data = await state.get_data()
    name = data['name']
    mail = data['mail']
    group = data['group']
    data_begin = data['data_begin']
    data_end = data['data_end']
    title = data['title']

    msg = f'Проверьте данные:\n\n' \
          f'<b>Опрос: </b>{title}\n' \
          f'<b>Начало: </b>{data_begin}\n' \
          f'<b>Конец: </b>{data_end}\n\n' \
          f'<b>ФИО: </b>{name}\n' \
          f'<b>Почта: </b>{mail}\n' \
          f'<b>Номер группы: </b>{group}'
    await bot.send_message(message.from_user.id, msg)
    msg = "Данные правильные?"
    await bot.send_message(message.from_user.id, msg, reply_markup=finish_registration_keyboard)
    await state.set_state(AuthorisedSurveyState.REGISTERED)


async def handle_request_exception(message: Message, bot: Bot, state: FSMContext, exception: Exception):
    if isinstance(exception, requests.exceptions.HTTPError):
        if exception.response.status_code == 404:
            await bot.send_message(message.from_user.id, "Опрос не найден, введите другой код!",
                                   reply_markup=enter_code_keyboard)
            await state.clear()
            await state.set_state(RegistrationState.GET_CODE)
        else:
            await bot.send_message(message.from_user.id, "Неизвестная ошибка, попробуйте перезапустить бота")
            await state.clear()
    else:
        await bot.send_message(message.from_user.id, "Неизвестная ошибка, попробуйте перезапустить бота")
        await state.clear()
