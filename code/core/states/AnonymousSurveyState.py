from aiogram.fsm.state import StatesGroup, State


class AnonymousSurveyState(StatesGroup):
    REGISTERED = State()
    WAITING = State()
    TAKING_SURVEY = State()
    MULTIPLE_ANSWER_WAITING = State()
    TEXT_ANSWER_WAITING = State()