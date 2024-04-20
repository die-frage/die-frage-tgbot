from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import requests

# Keyboards
from core.keybords.inline_boards import survey_menu_keyboard, next_question_keyboard, \
    next_and_back_question_keyboard, back_question_keyboard

# URLs
url_student_add_answer_auth = 'http://localhost:8787/api/answer/authorised'
url_student_add_answer_anonymous = 'http://localhost:8787/api/answer/anonymous'


async def handler_of_start_survey(message: Message, bot: Bot, state: FSMContext):
    msg = "Что бы вы хотели сделать?"
    await bot.send_message(message.from_user.id, msg, reply_markup=survey_menu_keyboard)


async def handler_of_anonymous_with_no_choice_answer(message: Message, bot: Bot, state: FSMContext):
    survey_data = await state.get_data()
    answer = message.text
    question_index = survey_data['current_question']
    survey_id = survey_data['survey_id']
    await process_of_anonymous_with_no_choice_answer(message, bot, state, survey_id, question_index, answer)


async def handler_of_authenticated_with_no_choice_answer(message: Message, bot: Bot, state: FSMContext):
    survey_data = await state.get_data()
    answer = message.text
    question_index = survey_data['current_question']
    student_id = survey_data['student_id']
    size_question = survey_data['size_questions']
    survey_id = survey_data['survey_id']
    await process_of_authenticated_with_no_choice_answer(message, bot, state, survey_id, student_id, question_index, answer, size_question)


async def process_of_anonymous_with_choice_answer(call: CallbackQuery, survey_id: int, question_index: int,
                                                  answer_index: int, answer: str):
    params = create_for_anonymous_params(survey_id, question_index, answer)

    try:
        response = requests.post(url_student_add_answer_anonymous, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

    msg = "Ответ записан успешно.\nСледующий вопрос:"
    await call.message.answer(msg, reply_markup=next_question_keyboard)


async def process_of_anonymous_with_no_choice_answer(message: Message, bot: Bot, state: FSMContext, survey_id: int,
                                                     question_index: int, answer: str):
    params = create_for_anonymous_params(survey_id, question_index, answer)

    try:
        response = requests.post(url_student_add_answer_anonymous, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

    msg = "Ответ записан успешно.\nСледующий вопрос:"
    await bot.send_message(message.from_user.id, msg, reply_markup=next_question_keyboard)


async def process_of_authenticated_with_choice_answer(call: CallbackQuery, survey_id: int, student_id: int,
                                                      question_id: int, answer_index: int,
                                                      answer: str, size_question: int):
    params = create_for_authenticated_params(survey_id, student_id, question_id, answer)

    try:
        response = requests.post(url_student_add_answer_auth, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

    msg = "Ответ записан успешно!"
    if question_id == 0:
        await call.message.answer(msg, reply_markup=next_question_keyboard)
    elif question_id + 1 < size_question:
        await call.message.answer(msg, reply_markup=next_and_back_question_keyboard)
    else:
        await call.message.answer(msg, reply_markup=back_question_keyboard)


async def process_of_authenticated_with_no_choice_answer(message: Message, bot: Bot, state: FSMContext,
                                                         survey_id: int, student_id: int, question_id: int,
                                                         answer: str, size_question: int):
    params = create_for_authenticated_params(survey_id, student_id, question_id, answer)
    try:
        response = requests.post(url_student_add_answer_auth, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

    msg = "Ответ записан успешно"
    if question_id == 0:
        await bot.send_message(message.from_user.id, msg, reply_markup=next_question_keyboard)
    elif question_id + 1 < size_question:
        await bot.send_message(message.from_user.id, msg, reply_markup=next_and_back_question_keyboard)
    else:
        await bot.send_message(message.from_user.id, msg, reply_markup=back_question_keyboard)


def create_for_authenticated_params(survey_id, student_id, question_index, answer):
    response = "{\"question_id\":" + str(question_index) + \
               ", \"points\":" + str(0) + \
               ", \"responses\":[" + "\"" + str(answer) + "\"" + "]}"

    params = {
        'survey_id': survey_id,
        'student_id': student_id,
        'response': response
    }

    return params


def create_for_anonymous_params(survey_id, question_index, answer):
    response = "{\"question_id\":" + str(question_index) + \
               ", \"points\":" + str(0) + \
               ", \"responses\":[" + "\"" + str(answer) + "\"" + "]}"

    params = {
        'survey_id': survey_id,
        'response': response
    }

    return params