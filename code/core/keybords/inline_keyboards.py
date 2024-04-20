from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

enter_code_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Ввести код',
                callback_data='start_registration',
            )
        ]
    ]
)

finish_registration_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data='finish_registration',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Нет',
                callback_data='start_registration',
            )
        ]
    ]
)

survey_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Проверить опрос',
                callback_data='update_survey',
            )
        ],
        [
            InlineKeyboardButton(
                text='Ввести код',
                callback_data='start_registration',
            )
        ]
    ]
)

start_survey_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Начать опрос',
                callback_data='start_survey',
            )
        ]
    ]
)

next_question_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='дальше >>',
                callback_data='next_question',
            )
        ]
    ]
)

back_question_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='<< назад',
                callback_data='back_question',
            )
        ],
        [
            InlineKeyboardButton(
                text='Завершить опрос?',
                callback_data='finish_survey',
            )
        ]
    ]
)

next_and_back_question_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='<< назад',
                callback_data='back_question',
            ),
            InlineKeyboardButton(
                text='дальше >>',
                callback_data='next_question',
            )
        ]
    ]
)
