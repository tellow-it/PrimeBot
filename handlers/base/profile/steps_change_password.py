from aiogram.fsm.state import StatesGroup, State


class ChangePasswordForm(StatesGroup):
    GET_DURING_PASSWORD = State()
    GET_NEW_PASSWORD = State()
