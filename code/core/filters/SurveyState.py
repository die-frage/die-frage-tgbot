from aiogram.fsm.state import StatesGroup, State


class SurveyState(StatesGroup):
    READY_ANONYMOUS = State()
    READY_NOT_ANONYMOUS = State()
    STARTED = State()
    GOING = State()
    STOPPED = State()
    FINISHED = State()