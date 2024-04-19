from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import requests

from core.filters.RegistrationState import RegistrationState
from core.filters.SurveyState import SurveyState

url = 'http://localhost:8787/api/student/registration'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}


async def registration(call: CallbackQuery, bot: Bot, state: FSMContext):
    if call.data == 'start_registration':
        await state.clear()
        await call.message.answer("Введите код:")
        await state.set_state(RegistrationState.GET_CODE)

    if call.data == 'finish_registration':
        if await state.get_state() == SurveyState.READY_NOT_ANONYMOUS:
            data = await state.get_data()
            student_data = {
                'email': data['mail'],
                'group_number': data['group'],
                'name': data['name']
            }

            response = requests.post(url, json=student_data, headers=headers)
            if response.status_code == 200:
                await call.answer("Регистрация прошла успешно!")
                await call.message.answer("Регистрация прошла успешно!")
            else:
                error_info = response.json()
                if error_info['message'] == 'INVALID_EMAIL_FORMAT':
                    await call.answer("Ошибка!")
                    await call.message.answer("Неверный формат почты!")
                else:
                    await call.answer("Ошибка!")
                    await call.message.answer("Неизвестная ошибка, попробуйте перезапустить код")
            await state.clear()
        else:
            await call.answer("Регистрация прошла успешно!")
            await call.message.answer("Регистрация прошла успешно!")
