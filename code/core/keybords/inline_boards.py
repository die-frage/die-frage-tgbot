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
                text='Зарегистрироваться',
                callback_data='finish_registration',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Сбросить данные',
                callback_data='start_registration',
            )
        ]
    ]
)
