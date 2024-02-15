from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_kb() -> InlineKeyboardMarkup:
    """Get kb for main menu
    """
    ikb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Кнопка 1', callback_data='cb_btn_1_main'),
    ]])
    return ikb
