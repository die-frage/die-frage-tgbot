from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from datetime import datetime

from core.states.RegistrationState import RegistrationState
from core.states.SurveyState import SurveyState
from core.handlers.survey_handlers import process_of_authenticated_with_choice_answer
from core.keybords.inline_keyboards import survey_menu_keyboard, start_survey_keyboard, \
    enter_code_keyboard, exit_from_survey_keyboard

# Urls
url_register_student = 'http://localhost:8787/api/student/registration'
url_update_student = 'http://localhost:8787/api/student/update'
url_get_student_by_email = 'http://localhost:8787/api/student/'
url_get_student_by_chat_id = 'http://localhost:8787/api/student/by_chat_id/'
url_register_user_for_survey = 'http://localhost:8060/api/telegram/add/record'
url_get_record = 'http://localhost:8060/api/telegram/record'
url_get_survey = 'http://localhost:8787/api/survey/telegram'
url_delete_record = 'http://localhost:8060/api/telegram/record'
url_start_survey = 'http://localhost:8060/api/telegram/start/record'
url_stop_survey = 'http://localhost:8060/api/telegram/stop/record'

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}


async def start_registration(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Введите код:")
    await state.set_state(RegistrationState.GET_CODE)


async def register_authorized_user(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_updating = data.get('is_updating', False)
    if is_updating:
        student_data = {
            'email': data['mail'],
            'group_number': data['group'],
            'chat_id': str(call.message.chat.id),
            'name': data['name']
        }
        response = requests.post(url_update_student, json=student_data, headers=headers)
        if response.status_code != 200:
            await call.answer("Ошибка!")
            await call.message.answer("Вы уже зарегистрированы на опрос")
            await state.clear()
    res = await get_student_by_email(call, state, data['mail'])
    if not res:
        student_data = {
            'email': data['mail'],
            'group_number': data['group'],
            'chat_id': str(call.message.chat.id),
            'name': data['name']
        }
        response = requests.post(url_register_student, json=student_data, headers=headers)
        if response.status_code == 200:
            params = '?chat_id=' + str(call.message.chat.id) + \
                     '&survey_id=' + str(data['survey_id'])
            await register_user_for_survey(call, state, params)
        else:
            await call.answer("Ошибка!")
            await call.message.answer("Вы уже зарегистрированы на опрос")
            await state.clear()


async def register_user_for_survey(call: CallbackQuery, state: FSMContext, params):
    url = url_register_user_for_survey + params
    print(url)
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        await call.answer("Регистрация прошла успешно!")
        await call.message.answer("Регистрация прошла успешно!", reply_markup=survey_menu_keyboard)
        await state.set_state(SurveyState.WAITING)
    else:
        if response.json()['code'] == 'USER_ALREADY_EXISTS':
            await call.answer("Уже зарегистрированы!")
            msg = "Чтобы зарегистрироваться на новый опрос, необходимо выйти из старого."
            await call.message.answer(msg, reply_markup=exit_from_survey_keyboard)
            await state.clear()
        elif response.json()['code'] == 'SURVEY_NOT_FOUND':
            await call.answer("Опрос не найден!")
            msg = "Чтобы зарегистрироваться на новый опрос, воспользуйтесь кнопками ниже: "
            await call.message.answer(msg, reply_markup=exit_from_survey_keyboard)
            await state.clear()
        else:
            print(response.json())
            await call.answer("Ошибка!")
            await call.message.answer("Неизвестная ошибка, попробуйте перезапустить бота.")
            await state.clear()


async def get_student_by_email(call: CallbackQuery, state: FSMContext, email: str):
    data = await state.get_data()
    url = url_get_student_by_email
    params = {
        'email': email,
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        await call.message.answer("Вы авторизированны.")
        params = '?chat_id=' + str(call.message.chat.id) + \
                 '&survey_id=' + str(data['survey_id'])
        await register_user_for_survey(call, state, params)
        return True
    else:
        return False


async def check_user_registration(call: CallbackQuery, state: FSMContext):
    response = requests.get(f'{url_get_record}/{call.message.chat.id}', headers=headers)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        survey_id = data['survey_id']
        await state.update_data(survey_id=survey_id)
        return data
    else:
        await call.answer("Ошибка!")
        await call.message.answer("Вы не зарегистрированы на опрос.")
        await state.set_state(RegistrationState.GET_CODE)
        return None


async def get_survey(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    survey_id = data['survey_id']
    url = f'{url_get_survey}/{survey_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data_response = response.json()
        begin_datetime = datetime.fromisoformat(data_response['date_begin'][:-6])
        end_datetime = datetime.fromisoformat(data_response['date_end'][:-6])
        begin_formatted = begin_datetime.strftime('%H:%M %d.%m.%Y')
        end_formatted = end_datetime.strftime('%H:%M %d.%m.%Y')
        title = data_response['title']
        current_time = datetime.now()
        if current_time < begin_datetime:
            msg = f'ОПРОС ЕЩЕ НЕ НАЧИЛСЯ\n\n' \
                  f'<b>Опрос: </b>{title}\n' \
                  f'<b>Начало: </b>{begin_formatted}\n' \
                  f'<b>Конец: </b>{end_formatted}\n\n' \
                  f'<b>Статус: </b>зарегистрирован'
            await call.answer("ОПРОС ЕЩЕ НЕ НАЧИЛСЯ")
            await call.message.answer(msg, reply_markup=survey_menu_keyboard)
        else:
            remaining_time = (end_datetime - current_time).total_seconds() // 60
            survey_details_msg = f'<b>Опрос: </b>{title}\n' \
                                 f'<b>Начало: </b>{begin_formatted}\n' \
                                 f'<b>Конец: </b>{end_formatted}\n' \
                                 f'<b>Статус: </b>зарегистрирован\n' \
                                 f'Оставшееся время: {int(remaining_time)} минут'
            attention_msg = 'Внимание! ОПРОС МОЖНО НАЧАТЬ ПРОХОДИТЬ. ' \
                            'После нажатия на кнопку "Начать опрос" ' \
                            'отменить это действие будет нельзя.'
            await call.message.answer(survey_details_msg)
            await call.message.answer(attention_msg, reply_markup=start_survey_keyboard)
    else:
        await call.answer("Ошибка!")
        await call.message.answer("Неизвестная ошибка, попробуйте перезапустить бота.")
        await state.clear()


async def start_first_question(call: CallbackQuery, state: FSMContext, questions):
    await state.update_data(questions=questions)
    await state.update_data(size_questions=len(questions))
    await state.update_data(current_question=0)
    await state.set_state(SurveyState.TAKING_SURVEY)
    survey_data = await state.get_data()
    current_question = survey_data['current_question']
    question = survey_data['questions'][current_question]
    question_text = question['question']
    question_type = question['type_question']
    points = question['points']
    msg = f"Вопрос #<b>{current_question + 1}</b>\n"
    if points and points != 0:
        msg += f"Количество баллов: {points}\n"
    if question['time_limit_sec']:
        minutes = question['time_limit_sec'] // 60
        seconds = question['time_limit_sec'] % 60
        msg += f"Время ответа на вопрос: {minutes} минут {seconds} сек\n"
    msg += f"<b>\n{question_text}</b>\n"
    msg += f"{'Выбрать правильный ответ' if question_type == 'MULTIPLE' else 'Записать решение'}\n"

    if question_type == 'MULTIPLE':
        incorrect_answers = question['incorrect_answers']
        correct_answer = question['correct_answers']
        options = incorrect_answers + correct_answer
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=option, callback_data=f'answer_{index}_{option}')] for
                             index, option in enumerate(options, 1)])
        await state.set_state(SurveyState.MULTIPLE_ANSWER_WAITING)
        await call.message.answer(msg, reply_markup=reply_markup)
    else:
        await state.set_state(SurveyState.TEXT_ANSWER_WAITING)
        await call.message.answer(msg)


async def start_next_question(call: CallbackQuery, state: FSMContext):
    survey_data = await state.get_data()
    current_question = survey_data['current_question']
    if current_question + 1 == survey_data['size_questions']:
        await finish_survey(call, state)
    else:
        current_question = current_question + 1
        question = survey_data['questions'][current_question]
        await state.update_data(current_question=current_question)
        question_text = question['question']
        question_type = question['type_question']
        points = question['points']

        msg = f"Вопрос #<b>{current_question + 1}</b>\n"
        if points and points != 0:
            msg += f"Количество баллов: {points}\n"
        if question['time_limit_sec']:
            minutes = question['time_limit_sec'] // 60
            seconds = question['time_limit_sec'] % 60
            if minutes == 0:
                msg += f"Время ответа на вопрос: {seconds} сек\n"
            else:
                msg += f"Время ответа на вопрос: {minutes} минут {seconds} сек\n"
        msg += f"<b>\n{question_text}</b>\n"
        msg += f"{'Выбрать правильный ответ' if question_type == 'MULTIPLE' else 'Записать решение'}\n"

        if question_type == 'MULTIPLE':
            incorrect_answers = question['incorrect_answers']
            correct_answer = question['correct_answers']
            options = incorrect_answers + correct_answer
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=option, callback_data=f'answer_{index}_{option}')] for
                                 index, option in enumerate(options, 1)])
            await call.message.answer(msg, reply_markup=reply_markup)
            await state.set_state(SurveyState.MULTIPLE_ANSWER_WAITING)
        else:
            await state.set_state(SurveyState.TEXT_ANSWER_WAITING)
            await call.message.answer(msg)


async def start_survey(call: CallbackQuery, state: FSMContext):
    url = f'{url_start_survey}/{call.from_user.id}'
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        if response.json()['code'] == 'USER_ALREADY_EXISTS':
            await call.answer("Ошибка!")
            await call.message.answer("Вы уже проходили данный опрос!")
            await state.clear()
            msg = "Опрос завершен!\n" \
                  "Спасибо за участие!"
            await call.message.answer(msg)
            await call.answer("Опрос завершен!")
            msg = "Это телеграм бот для <b>проведения опросов</b>"
            await call.message.answer(msg)
            msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
            await call.message.answer(msg)
            msg = "Для прохождения опроса сканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
                  "нажав на кнопку\n "
            await call.message.answer(msg, reply_markup=enter_code_keyboard)
        else:
            await call.answer("Ошибка!")
            await call.message.answer("Неизвестная ошибка, попробуйте перезапустить бота.")
            await state.clear()


async def get_results(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    answers = data['answers']
    questions = data['questions']
    total_score = 0
    message = ""

    for question in questions:
        question_text = question['question']
        if len(question['correct_answers']) < 1:
            correct_answer = ''
        else:
            correct_answer = question['correct_answers'][0]
        score = question.get('points', 0)

        found_answer = None
        counter = 0
        for answer in answers:
            counter = counter + 1
            if answer.get('question_id') == question['question_id']:
                found_answer = answer.get('response')
                break

        if found_answer is None:
            message += f"<b>#{counter} Вопрос: {question_text}</b>\n"
            message += "Ваш ответ: Не дан\n"
            if question['type_question'] == 'MULTIPLE':
                message += f"Правильный ответ: {correct_answer}\n"
                message += "Баллы: 0/{}\n\n".format(score)
            else:
                message += "Баллы: 0/{}\n\n".format(score)

        else:
            if found_answer == correct_answer:
                total_score += score
            message += f"<b>#{counter} Вопрос: {question_text}</b>\n"
            message += f"Ваш ответ: {found_answer}\n"
            if question['type_question'] == 'MULTIPLE':
                message += f"Правильный ответ: {correct_answer}\n"
                message += "Баллы: {}/{}\n\n".format(score if found_answer == correct_answer else 0, score)
            else:
                message += "Баллы: 0/{}\n\n".format(score)

    message += f"\nИтого Вы набрали: {total_score}/{sum(question.get('points', 0) for question in questions)} баллов."

    await call.message.answer(message)


async def stop_survey(call: CallbackQuery, state: FSMContext):
    url = f'{url_stop_survey}/{call.from_user.id}'
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        await call.answer("Результаты:")
        await get_results(call, state)
        await state.clear()
    else:
        if response.json()['code'] == 'USER_ALREADY_EXISTS':
            await call.answer("Ошибка!")
            await call.message.answer("Вы еще не прошли данный опрос!", reply_markup=survey_menu_keyboard)
            await state.clear()
        else:
            await call.answer("Ошибка!")
            await call.message.answer("Неизвестная ошибка, попробуйте перезапустить бота.")
            await state.clear()


async def finish_survey(call: CallbackQuery, state: FSMContext):
    await stop_survey(call, state)
    await state.clear()
    msg = "Опрос завершен!\n" \
          "Спасибо за участие!"
    await call.message.answer(msg)
    await call.answer("Опрос завершен!")
    msg = "Это телеграм бот для <b>проведения опросов</b>"
    await call.message.answer(msg)
    msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
    await call.message.answer(msg)
    msg = "Для прохождения опроса сканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
          "нажав на кнопку\n "
    await call.message.answer(msg, reply_markup=enter_code_keyboard)


async def start_back_question(call: CallbackQuery, state: FSMContext):
    survey_data = await state.get_data()
    current_question = survey_data['current_question']
    current_question = current_question - 1
    question = survey_data['questions'][current_question]
    await state.update_data(current_question=current_question)
    question_text = question['question']
    question_type = question['type_question']
    points = question['points']
    msg = f"Вопрос #<b>{current_question + 1}</b>\n"
    if points and points != 0:
        msg += f"Количество баллов: {points}\n"
    if question['time_limit_sec']:
        minutes = question['time_limit_sec'] // 60
        seconds = question['time_limit_sec'] % 60
        msg += f"Время ответа на вопрос: {minutes} минут {seconds} сек\n"
    msg += f"<b>\n{question_text}</b>\n"
    msg += f"{'Выбрать правильный ответ' if question_type == 'MULTIPLE' else 'Записать решение'}\n"

    if question_type == 'MULTIPLE':
        incorrect_answers = question['incorrect_answers']
        correct_answer = question['correct_answers']
        options = incorrect_answers + correct_answer
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=option, callback_data=f'answer_{index}_{option}')] for
                             index, option in enumerate(options, 1)])
        await call.message.answer(msg, reply_markup=reply_markup)
        await state.set_state(SurveyState.MULTIPLE_ANSWER_WAITING)
    else:
        await call.message.answer(msg)
        await state.set_state(SurveyState.TEXT_ANSWER_WAITING)


async def process_callback_with_choice_answer(call: CallbackQuery, state: FSMContext, user_state):
    survey_data = await state.get_data()
    if call.data.startswith('answer_'):
        data = call.data.split('_')
        answer_index = int(data[1])
        answer = data[2]
        if user_state == SurveyState.MULTIPLE_ANSWER_WAITING:
            await process_of_authenticated_with_choice_answer(call, state, survey_data['survey_id'],
                                                              survey_data['student_id'],
                                                              survey_data['current_question'], answer_index,
                                                              answer, survey_data['size_questions'])
    if survey_data['current_question'] + 1 == survey_data['size_questions']:
        await finish_survey(call, state)


async def exit_from_survey(call: CallbackQuery, state: FSMContext):
    response = requests.delete(f'{url_get_record}/{call.message.chat.id}', headers=headers)
    if response.status_code == 200:
        msg = "Это телеграм бот для <b>проведения опросов</b>"
        await call.message.answer(msg)
        msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
        await call.message.answer(msg)
        msg = "Для прохождения опроса сканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
              "нажав на кнопку\n "
        await call.message.answer(msg, reply_markup=enter_code_keyboard)
    else:
        await call.answer("Ошибка!")
        await call.message.answer("Неизвестная ошибка, попробуйте перезапустить бота.")
        await state.clear()


async def callback(call: CallbackQuery, bot: Bot, state: FSMContext):

    if call.data == 'start_registration':
        await start_registration(call, state)

    if call.data == 'finish_registration':
        if await state.get_state() == SurveyState.REGISTERED:
            await register_authorized_user(call, state)

    if call.data == 'update_survey':
        if await check_user_registration(call, state) is not None:
            await get_survey(call, state)

    if call.data == 'start_survey':
        response_data = await check_user_registration(call, state)
        if response_data is not None:
            survey_id = response_data['survey_id']
            await state.update_data(survey_id=survey_id)
            if 'student_id' in response_data:
                student_id = response_data['student_id']
                await state.update_data(student_id=student_id)
            else :
                response = requests.get(url_get_student_by_chat_id + str(call.message.chat.id), headers=headers)
                tmp_data = response.json()
                print(tmp_data)
                student_id = tmp_data['student_id']
                await state.update_data(student_id=student_id)
            url = f'{url_get_survey}/{survey_id}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                await start_survey(call, state)
                data = response.json()
                questions = data['questions']
                data = await state.get_data()
                student_id = data['student_id']
                await state.update_data(student_id=student_id)
                await start_first_question(call, state, questions)

    if call.data == 'finish_survey':
        await finish_survey(call, state)

    if call.data == 'exit_from_survey':
        if await check_user_registration(call, state) is not None:
            await exit_from_survey(call, state)

    user_state = await state.get_state()
    is_authorised_choice = user_state == SurveyState.MULTIPLE_ANSWER_WAITING
    is_authorised_no_choice = user_state == SurveyState.TEXT_ANSWER_WAITING

    if call.data == 'next_question':
        if is_authorised_choice or is_authorised_no_choice:
            await start_next_question(call, state)
    elif call.data == 'back_question':
        if is_authorised_no_choice or is_authorised_choice:
            await start_back_question(call, state)
    elif is_authorised_choice:
        await process_callback_with_choice_answer(call, state, user_state)
