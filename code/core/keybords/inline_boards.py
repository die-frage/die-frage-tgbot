from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='Ввести код',
        callback_data='start_registration',
    )]]
)

main_final_keyboard = InlineKeyboardMarkup(
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

main_start_survey_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text='Начать опрос',
        callback_data='start_survey',
    )]]
)
