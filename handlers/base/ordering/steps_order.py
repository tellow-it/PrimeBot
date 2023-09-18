from aiogram.fsm.state import StatesGroup, State


class OrderForm(StatesGroup):
    GET_ORDER_NAME = State()
    GET_BUILDING = State()
    GET_SYSTEM = State()
    GET_IMPORTANT = State()
    GET_MATERIAL_NAME = State()
    GET_MATERIAL_QUANTITY = State()
    GET_MATERIAL_MORE = State()
    GET_DESCRIPTION = State()
    GET_STATUS = State()
