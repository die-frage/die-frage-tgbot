from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    GET_INIT = State()
    GET_CODE = State()
    GET_NAME = State()
    GET_MAIL = State()
    GET_GROUP = State()
