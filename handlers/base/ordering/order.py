from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiohttp import ClientConnectorError

from api.base.order import get_orders, get_buildings, get_data_by_param
from handlers.auth.steps_auth import AuthForm
from aiogram.types import Message, ReplyKeyboardRemove
from db.misc import get_value, set_value
from handlers.base.ordering.steps_order import OrderForm
from keyboards.base.order import order_menu_kbd, params_kbd
from keyboards.menu import cancel_kbd
from keyboards.menu import menu_kbd

from api.auth.authentication import login, decode_code
from utils.auth import check_auth

order_router = Router()


@order_router.message(F.text == "Отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup=ReplyKeyboardRemove(),
    )


@order_router.message(Command(commands=['order_menu']))
async def order_menu(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await message.answer("Заявки", reply_markup=order_menu_kbd())
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@order_router.message(Command(commands=['orders']))
async def user_orders(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            access_token = await get_value(f'{message.from_user.id}:access_token')
            _, user_id = await decode_code(access_token=access_token.decode())
            _, orders = await get_orders(access_token=access_token.decode(), user_id=user_id)
            await message.answer("Список заявок:")
            if orders:
                format_orders = "\n\n".join(
                    [f"Заявка: {order['order_name']}\n"
                     f"Объект: {order['building']['building_name']}\n"
                     f"Статус: {order['status']['status_name']}\n"
                     f"Последние изменения: {order['modified_at'][:10]}\n"
                     f"Ожидается: {order['expected_time'][:10]}"
                     for order in orders])
                await message.answer(format_orders, reply_markup=order_menu_kbd())
            else:
                await message.answer("У вас нету заявок", reply_markup=order_menu_kbd())
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@order_router.message(Command(commands=['create_order']))
async def create_order(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await message.answer("Создание заявки")
            await message.answer("Укажите название заявки", reply_markup=cancel_kbd())
            await state.set_state(OrderForm.GET_ORDER_NAME)
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@order_router.message(OrderForm.GET_ORDER_NAME)
async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            access_token = await get_value(f'{message.from_user.id}:access_token')
            await message.answer(f"Название заявки: {message.text}")
            await state.update_data(order_name=message.text)
            _, available_buildings = await get_buildings(access_token=access_token)
            await state.update_data(available_buildings=available_buildings)
            await message.answer('Выберете объект',
                                 reply_markup=params_kbd(param_name="building", data=available_buildings))
            await state.set_state(OrderForm.GET_BUILDING)
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@order_router.message(OrderForm.GET_BUILDING)
async def process_getting_building(message: types.Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        available_buildings = state_data["available_buildings"]
        await message.answer(f"Название объекта: {message.text}")
        if message.text in [build["building_name"] for build in available_buildings]:
            building_id = [build for build in available_buildings if build["building_name"] == message.text][0]["id"]
            await state.update_data(building_id=building_id)
            access_token = await get_value(f'{message.from_user.id}:access_token')
            _, available_systems = await get_data_by_param(access_token=access_token, param="system")
            await state.update_data(available_systems=available_systems)
            await message.answer('Выберете систему', reply_markup=params_kbd(param_name="system", data=available_systems))
            await state.set_state(OrderForm.GET_SYSTEM)
        else:
            await message.answer("Вы выбрали объект, которого не существуют, попробуйте еще раз",
                                 reply_markup=params_kbd(param_name="building", data=available_buildings))
            await state.set_state(OrderForm.GET_BUILDING)
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()

#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#
#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#
#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#
#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#
#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#
#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
#
#
# @order_router.message(OrderForm.GET_ORDER_NAME)
# async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
#     try:
#         await message.answer(f"Название заявки: {message.text}")
#         await state.update_data(order_name=message.text)
#         await message.answer('Выберете объект', reply_markup=params_kbd(param_name="building", data=data))
#         await state.set_state(AuthForm.GET_PASSWORD)
#     except (Exception, ClientConnectorError):
#         await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.clear()
