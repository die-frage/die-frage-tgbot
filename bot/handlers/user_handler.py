from aiogram import types, Dispatcher
from aiogram.filters import CommandStart

from bot.keyboards.user_keyboards import get_main_kb

async def cmd_start(msg: types.Message) -> None:
    """Command start
    """
    
    reply_text = 'Привет, как твои дела?\n'
    reply_text += f'Твое имя - {msg.from_user.first_name}!'
    await msg.reply(
        text=reply_text,
        reply_markup=get_main_kb()
    )

def register_user_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, CommandStart())
    
