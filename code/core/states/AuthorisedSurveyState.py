from aiogram.fsm.state import StatesGroup, State


class AuthorisedSurveyState(StatesGroup):
    TAKING_SURVEY = State()
    REGISTERED = State()
    WAITING = State()
    MULTIPLE_ANSWER_WAITING = State()
    TEXT_ANSWER_WAITING = State()
    ANSWERED = State()
