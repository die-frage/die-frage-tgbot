from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from datetime import datetime

from core.filters.RegistrationState import RegistrationState
from core.filters.SurveyAuthorised import SurveyAuthorised
from core.filters.SurveyAnonymous import SurveyAnonymous
from core.handlers.waiting_survey import process_answer_MULTIPLE_CHOICE, process_answer_auth_MULTIPLE_CHOICE
from core.keybords.inline_boards import waiting_survey_keyboard, main_start_survey_keyboard, main_start_keyboard

url_student = 'http://localhost:8787/api/student/registration'
url_record = 'http://localhost:8787/api/telegram/add/record'
url_get_record = 'http://localhost:8787/api/telegram/record'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}


async def registration(call: CallbackQuery, bot: Bot, state: FSMContext):
    if call.data == 'start_registration':
        await state.clear()
        await call.message.answer("Введите код:")
        await state.set_state(RegistrationState.GET_CODE)
    data = await state.get_data()
    if call.data == 'finish_registration':
        if await state.get_state() == SurveyAuthorised.REGISTERED:
            student_data = {
                'email': data['mail'],
                'group_number': data['group'],
                'name': data['name']
            }
            response = requests.post(url_student, json=student_data, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                params = '?chat_id=' + str(call.message.chat.id) + \
                         '&survey_id=' + str(data['survey_id']) + \
                         '&student_id=' + str(response_data['student_id'])
                response = requests.post(url_record + params, headers=headers)
                print(response.json())
                if response.status_code == 200:
                    await call.answer("Регистрация прошла успешно!")
                    await call.message.answer("Регистрация прошла успешно!", reply_markup=waiting_survey_keyboard)
                    await state.set_state(SurveyAuthorised.WAITING)
                else:
                    await call.answer("Ошибка!")
                    await call.message.answer("Неизвестная ошибка, попробуйте перезапустить код")
                    await state.clear()
            else:
                await call.answer("Ошибка!")
                await call.message.answer("Неизвестная ошибка, попробуйте перезапустить код")
                await state.clear()

        else:
            params = '?chat_id=' + str(call.message.chat.id) + \
                     '&survey_id=' + str(data['survey_id'])
            response = requests.post(url_record + params, headers=headers)
            if response.status_code == 200:
                await call.answer("Регистрация прошла успешно!")
                await call.message.answer("Регистрация прошла успешно!", reply_markup=waiting_survey_keyboard)
                await state.set_state(SurveyAnonymous.WAITING)
            else:
                await call.answer("Ошибка!")
                await call.message.answer("Неизвестная ошибка, попробуйте перезапустить код")
                await state.clear()
    if call.data == 'update_survey':
        response = requests.get(url_get_record + '/' + str(call.message.chat.id), headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            survey_id = response_data['survey_id']
            await state.update_data(survey_id=survey_id)
            url = f'http://localhost:8787/api/survey/telegram/{survey_id}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                    data = response.json()
                    print(data)
                    begin_datetime = datetime.fromisoformat(data['date_begin'][:-6])
                    end_datetime = datetime.fromisoformat(data['date_end'][:-6])
                    begin_formatted = begin_datetime.strftime('%H:%M %d.%m.%Y')
                    end_formatted = end_datetime.strftime('%H:%M %d.%m.%Y')
                    title = data['title']
                    current_time = datetime.now()
                    if current_time < begin_datetime:
                        msg = f'ОПРОС ЕЩЕ НЕ НАЧИЛСЯ\n\n' \
                              f'<b>Опрос: </b>{title}\n' \
                              f'<b>Начало: </b>{begin_formatted}\n' \
                              f'<b>Конец: </b>{end_formatted}\n\n' \
                              f'<b>Статус: </b>зарегистрирован'
                        await call.answer("ОПРОС ЕЩЕ НЕ НАЧИЛСЯ")
                        await call.message.answer(msg, reply_markup=waiting_survey_keyboard)
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
                        instructions_msg = 'Важно! Если это не анонимный опрос, ' \
                                           'то вы можете переходить между вопросами с ' \
                                           'помощью кнопок вперед и назад. ' \
                                           'Иначе у вас будет всего одна попытка ответа ' \
                                           'на каждый вопрос. Кнопка "Начать опрос".'
                        await call.message.answer(survey_details_msg)
                        await call.message.answer(attention_msg)
                        await call.message.answer(instructions_msg, reply_markup=main_start_survey_keyboard)

            else:
                await call.answer("Ошибка!")
                await call.message.answer("Неизвестная ошибка, попробуйте перезапустить код")
                await state.clear()
        else:
            print(response.json())
            await call.answer("Ошибка!")
            await call.message.answer("Вы не зарегистрированы на опрос")
            await state.set_state(RegistrationState.GET_CODE)
    if call.data == 'start_survey':
        response = requests.get(url_get_record + '/' + str(call.message.chat.id), headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            survey_id = response_data['survey_id']
            await state.update_data(survey_id=survey_id)

            student_id = None
            if 'student_id' in response_data:
                student_id = response_data['student_id']
            url = f'http://localhost:8787/api/survey/telegram/{survey_id}'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                questions = data['questions']
                if data['anonymous']:
                    await state.update_data(questions=questions)
                    await state.update_data(size_questions=len(questions))
                    await state.update_data(current_question=0)
                    await state.set_state(SurveyAnonymous.TAKING_SURVEY)
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
                        msg += f"Время ответа на вопрос: {question['time_limit_sec'] // 60} минут {question['time_limit_sec'] % 60} сек\n"
                    msg += f"<b>\n{question_text}</b>\n"
                    msg += f"{'Выбрать правильный ответ' if question_type == 'MULTIPLE' else 'Записать решение'}\n"

                    if question_type == 'MULTIPLE':
                        incorrect_answers = question['incorrect_answers']
                        correct_answer = question['correct_answers']
                        options = incorrect_answers + correct_answer
                        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=option, callback_data=f'answer_{index}_{option}')] for index, option in enumerate(options, 1)])
                        await call.message.answer(msg, reply_markup=reply_markup)
                        await state.set_state(SurveyAnonymous.MULTIPLE_ANSWER_WAITING)
                    else:
                        await call.message.answer(msg)
                        await state.set_state(SurveyAnonymous.TEXT_ANSWER_WAITING)
                else:
                    await state.update_data(student_id=student_id)
                    await state.update_data(questions=questions)
                    await state.update_data(size_questions=len(questions))
                    await state.update_data(current_question=0)
                    await state.set_state(SurveyAuthorised.TAKING_SURVEY)
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
                        msg += f"Время ответа на вопрос: {question['time_limit_sec'] // 60} минут {question['time_limit_sec'] % 60} сек\n"
                    msg += f"<b>\n{question_text}</b>\n"
                    msg += f"{'Выбрать правильный ответ' if question_type == 'MULTIPLE' else 'Записать решение'}\n"

                    if question_type == 'MULTIPLE':
                        incorrect_answers = question['incorrect_answers']
                        correct_answer = question['correct_answers']
                        options = incorrect_answers + correct_answer
                        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=option, callback_data=f'answer_{index}_{option}')] for index, option in enumerate(options, 1)])
                        await call.message.answer(msg, reply_markup=reply_markup)
                        await state.set_state(SurveyAuthorised.MULTIPLE_ANSWER_WAITING)
                    else:
                        await call.message.answer(msg)
                        await state.set_state(SurveyAuthorised.TEXT_ANSWER_WAITING)
    user_state = await state.get_state()
    if call.data == 'next_question' and (user_state == SurveyAnonymous.TEXT_ANSWER_WAITING or user_state == SurveyAnonymous.MULTIPLE_ANSWER_WAITING):
        survey_data = await state.get_data()
        current_question = survey_data['current_question']
        if current_question + 1 == survey_data['size_questions']:
            await state.clear()
            msg = "Опрос завершен!\n" \
                  "Спасибо за участие!"
            await call.message.answer(msg)
            await call.answer("Опрос завершен!")
            msg = "Это телеграм бот для <b>проведения опросов</b>"
            await call.message.answer(msg)
            msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
            await call.message.answer(msg)
            msg = "Для прохождения опроса отсканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
                  "нажав на кнопку\n "
            await call.message.answer(msg, reply_markup=main_start_keyboard)
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
                msg += f"Время ответа на вопрос: {question['time_limit_sec'] // 60} минут {question['time_limit_sec'] % 60} сек\n"
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
                await state.set_state(SurveyAnonymous.MULTIPLE_ANSWER_WAITING)
            else:
                await call.message.answer(msg)
                await state.set_state(SurveyAnonymous.TEXT_ANSWER_WAITING)
    elif call.data == 'next_question' and (user_state == SurveyAuthorised.TEXT_ANSWER_WAITING or user_state == SurveyAuthorised.MULTIPLE_ANSWER_WAITING):
        survey_data = await state.get_data()
        current_question = survey_data['current_question']
        if current_question + 1 == survey_data['size_questions']:
            await state.clear()
            msg = "Опрос завершен!\n" \
                  "Спасибо за участие!"
            await call.message.answer(msg)
            await call.answer("Опрос завершен!")
            msg = "Это телеграм бот для <b>проведения опросов</b>"
            await call.message.answer(msg)
            msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
            await call.message.answer(msg)
            msg = "Для прохождения опроса отсканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
                  "нажав на кнопку\n "
            await call.message.answer(msg, reply_markup=main_start_keyboard)
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
                msg += f"Время ответа на вопрос: {question['time_limit_sec'] // 60} минут {question['time_limit_sec'] % 60} сек\n"
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
                await state.set_state(SurveyAuthorised.MULTIPLE_ANSWER_WAITING)
            else:
                await call.message.answer(msg)
                await state.set_state(SurveyAuthorised.TEXT_ANSWER_WAITING)
    elif call.data == 'back_question' and (user_state == SurveyAuthorised.TEXT_ANSWER_WAITING or user_state == SurveyAuthorised.MULTIPLE_ANSWER_WAITING):
        survey_data = await state.get_data()
        print(survey_data)
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
            msg += f"Время ответа на вопрос: {question['time_limit_sec'] // 60} минут {question['time_limit_sec'] % 60} сек\n"
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
            await state.set_state(SurveyAuthorised.MULTIPLE_ANSWER_WAITING)
        else:
            await call.message.answer(msg)
            await state.set_state(SurveyAuthorised.TEXT_ANSWER_WAITING)
    elif user_state == SurveyAnonymous.MULTIPLE_ANSWER_WAITING or user_state == SurveyAuthorised.MULTIPLE_ANSWER_WAITING:
        survey_data = await state.get_data()
        print(survey_data)
        if call.data.startswith('answer_'):
            data = call.data.split('_')
            answer_index = int(data[1])
            answer = data[2]
            if user_state == SurveyAnonymous.MULTIPLE_ANSWER_WAITING:
                await process_answer_MULTIPLE_CHOICE(call, survey_data['survey_id'], survey_data['current_question'], answer_index, answer)
            elif user_state == SurveyAuthorised.MULTIPLE_ANSWER_WAITING:
                await process_answer_auth_MULTIPLE_CHOICE(call, survey_data['survey_id'], survey_data['student_id'], survey_data['current_question'], answer_index, answer, survey_data['size_questions'])
        if survey_data['current_question'] + 1 == survey_data['size_questions']:
            await state.clear()
            msg = "Опрос завершен!\n" \
                  "Спасибо за участие!"
            await call.message.answer(msg)
            await call.answer("Опрос завершен!")

            msg = "Это телеграм бот для <b>проведения опросов</b>"
            await call.message.answer(msg)
            msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
            await call.message.answer(msg)
            msg = "Для прохождения опроса отсканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
                  "нажав на кнопку\n "
            await call.message.answer(msg, reply_markup=main_start_keyboard)
    if call.data == 'finish_survey':
        await state.clear()
        msg = "Опрос завершен!\n" \
              "Спасибо за участие!"
        await call.message.answer(msg)
        await call.answer("Опрос завершен!")
        msg = "Это телеграм бот для <b>проведения опросов</b>"
        await call.message.answer(msg)
        msg = "Для создания опроса воспользуйтесь конструктором: <a href='http://localhost:4200'>survey.com</a>"
        await call.message.answer(msg)
        msg = "Для прохождения опроса отсканируйте <i>QR-код</i> через камеру телефона или введите <i>код</i>, " \
              "нажав на кнопку\n "
        await call.message.answer(msg, reply_markup=main_start_keyboard)
