from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import requests

# URL для добавления ответа с авторизацией
url_student_add_answer_auth = 'http://localhost:8787/api/answer/authorised'

# URL для добавления анонимного ответа
url_student_add_answer_anonymous = 'http://localhost:8787/api/answer/anonymous'

from core.keybords.inline_boards import waiting_survey_keyboard, next_question_keyboard, \
    next_and_back_question_keyboard, back_question_keyboard


async def waiting_start_survey(message: Message, bot: Bot, state: FSMContext):
    msg = "Выберите, что Вы хотите сделать?"
    await bot.send_message(message.from_user.id, msg, reply_markup=waiting_survey_keyboard)


async def process_answer_MULTIPLE_CHOICE(call, survey_id, question_index, answer_index, answer):
    print(f'send answer: {question_index}, {answer_index}: {answer}')
    msg = "Ответ записан успешно.\nСледующий вопрос:"
    params_auth = {
        'survey_id': survey_id,
        'response': "{\"question_id\":" + str(question_index)+ ", \"points\":" + str(0) + ", \"responses\":[" + "\"" + str(answer) + "\"" + "]}"
    }
    response_auth = requests.post(url_student_add_answer_anonymous, params=params_auth)
    if response_auth.status_code == 200:
        print("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print(response_auth.json())
    await call.message.answer(msg, reply_markup=next_question_keyboard)


async def process_answer_TEXT(message: Message, bot: Bot, state: FSMContext,survey_id, question_index, answer):
    print(f'send answer: {question_index}, {answer}')
    msg = "Ответ записан успешно.\nСледующий вопрос:"
    params_auth = {
        'survey_id': survey_id,
        'response': "{\"question_id\":" + str(question_index)+ ", \"points\":" + str(0) + ", \"responses\":[" + "\"" + str(answer) + "\"" + "]}"
    }
    response_auth = requests.post(url_student_add_answer_anonymous, params=params_auth)
    if response_auth.status_code == 200:
        print("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print(response_auth.json())
    await bot.send_message(message.from_user.id, msg, reply_markup=next_question_keyboard)


async def answer_anonym_text_answer(message: Message, bot: Bot, state: FSMContext, survey_id):
    survey_data = await state.get_data()
    answer = message.text
    question_index = survey_data['current_question']
    await process_answer_TEXT(message, bot, state, survey_id, question_index, answer)


async def answer_auth_text_answer(message: Message, bot: Bot, state: FSMContext):
    survey_data = await state.get_data()
    answer = message.text
    question_index = survey_data['current_question']
    student_id = survey_data['student_id']
    size_question = survey_data['size_questions']
    survey_id = survey_data['survey_id']
    await process_answer_auth_TEXT(message, bot, state, survey_id, student_id, question_index, answer, size_question)


async def process_answer_auth_MULTIPLE_CHOICE(call, survey_id, student_id, question_index, answer_index, answer, size_question):
    params_auth = {
        'survey_id': survey_id,
        'student_id': student_id,
        'response': "{\"question_id\":" + str(question_index)+ ", \"points\":" + str(0) + ", \"responses\":[" + "\"" + str(answer) + "\"" + "]}"
    }
    response_auth = requests.post(url_student_add_answer_auth, params=params_auth)
    if response_auth.status_code == 200:
        print("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print(response_auth.json())

    msg = "Ответ записан успешно."
    if question_index == 0:
        await call.message.answer(msg, reply_markup=next_question_keyboard)
    elif question_index + 1 < size_question:
        await call.message.answer(msg, reply_markup=next_and_back_question_keyboard)
    else:
        await call.message.answer(msg, reply_markup=back_question_keyboard)


async def process_answer_auth_TEXT(message: Message, bot: Bot, state: FSMContext, survey_id, student_id, question_index, answer, size_question):
    params_auth = {
        'survey_id': survey_id,
        'student_id': student_id,
        'response': "{\"question_id\":" + str(question_index)+ ", \"points\":" + str(0) + ", \"responses\":[" + "\"" + str(answer) + "\"" + "]}"
    }
    response_auth = requests.post(url_student_add_answer_auth, params=params_auth)
    if response_auth.status_code == 200:
        print("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print(response_auth.json())

    msg = "Ответ записан успешно."
    if question_index == 0:
        await bot.send_message(message.from_user.id, msg, reply_markup=next_question_keyboard)
    elif question_index + 1 < size_question:
        await bot.send_message(message.from_user.id, msg, reply_markup=next_and_back_question_keyboard)
    else:
        await bot.send_message(message.from_user.id, msg, reply_markup=back_question_keyboard)
