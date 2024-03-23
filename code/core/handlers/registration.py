import requests
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from core.keybords.inline_boards import main_start_keyboard, main_final_keyboard
from datetime import datetime
from core.filters.RegistrationState import RegistrationState


async def get_start(message: Message, bot: Bot):
    msg = "Это телеграм бот для <b>проведения опросов</b>:\n\n 1. Если вы хотите создать опрос, то перейдите по " \
          "ссылке: <a href='http://localhost:4200'>survey.com</a>\n\n 2. Если вы хотите пройти опрос:\n\t\t - от " \
          "сканируйте <i>QR-код</i> через камеру телефона\n\t\t - введите <i>код</i>, нажав на кнопку Ввести код\n "
    await bot.send_message(message.from_user.id, msg, reply_markup=main_start_keyboard)


async def process_code(message: Message, bot: Bot, state: FSMContext):
    code = message.text
    url = f'http://localhost:8080/api/student/survey/{code}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Преобразование строк
        begin_datetime = datetime.fromisoformat(data['date_begin'][:-6])
        end_datetime = datetime.fromisoformat(data['date_end'][:-6])
        begin_formatted = begin_datetime.strftime('%H:%M %d.%m.%Y')
        end_formatted = end_datetime.strftime('%H:%M %d.%m.%Y')
        await state.update_data(code=code)
        await state.update_data(data_begin=begin_formatted)
        await state.update_data(data_end=end_formatted)
        await state.update_data(title=data['title'])
        await bot.send_message(message.from_user.id, "Введите <b>ФИО</b> ")
        await state.set_state(RegistrationState.GET_NAME)
    else:
        error_info = response.json()
        if error_info['message'] == 'SURVEY_NOT_FOUND':
            await bot.send_message(message.from_user.id, "Опрос не найден, проверьте код еще раз")
            await state.clear()
            await state.set_state(RegistrationState.GET_CODE)
        else:
            await bot.send_message(message.from_user.id, "Неизвестная ошибка, попробуйте перезапустить бота")
            await state.clear()


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

    msg = f'<u>Проверьте</u> <u>данные</u>:\n\n' \
          f'<b>Опрос: </b>{title}\n' \
          f'<b>Начало: </b>{data_begin}\n' \
          f'<b>Конец: </b>{data_end}\n\n' \
          f'<b>ФИО: </b>{name}\n' \
          f'<b>Почта: </b>{mail}\n' \
          f'<b>Номер группы: </b>{group}'
    await bot.send_message(message.from_user.id, msg)

    msg = "Если данные верны, то нажмите кнопку <b>начать опрос</b>\n" \
          "Если хотите изменить данные, то нажмите на кнопку <b>сбросить данные</b>"
    await bot.send_message(message.from_user.id, msg, reply_markup=main_final_keyboard)
