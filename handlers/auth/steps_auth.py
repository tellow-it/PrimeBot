from aiogram.fsm.state import StatesGroup, State


class AuthForm(StatesGroup):
    GET_PHONE = State()
    GET_PASSWORD = State()
