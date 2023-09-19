from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from api.base.order import get_orders, get_buildings, get_data_by_param, create_order_
from aiogram.types import Message, ReplyKeyboardRemove
from db.misc import get_value
from handlers.base.ordering.steps_order import OrderForm
from keyboards.base.order import order_menu_kbd, params_kbd, more_material_kbd, no_description_kbd
from keyboards.menu import cancel_kbd

from api.auth.authentication import decode_code
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
    except Exception as err:
        print(err)
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
                format_orders = ""
                for order in orders:
                    format_orders += f"Заявка: {order['order_name']}\n" \
                                     f"Объект: {order['building']['building_name']}\n" \
                                     f"Статус: {order['status']['status_name']}\n" \
                                     f"Последние изменения: {order['modified_at'][:10]}\n\n\n"
                await message.answer(format_orders, reply_markup=order_menu_kbd())
            else:
                await message.answer("У вас нету заявок", reply_markup=order_menu_kbd())
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@order_router.message(Command(commands=['create_order']))
async def create_order(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            access_token = await get_value(f'{message.from_user.id}:access_token')
            _, user_id = await decode_code(access_token=access_token.decode())
            await state.update_data(creator_id=user_id)
            await message.answer("Создание заявки")
            await message.answer("Укажите название заявки", reply_markup=cancel_kbd())
            await state.set_state(OrderForm.GET_ORDER_NAME)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
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
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
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
            await message.answer('Выберете систему',
                                 reply_markup=params_kbd(param_name="system", data=available_systems))
            await state.set_state(OrderForm.GET_SYSTEM)
        else:
            await message.answer("Вы выбрали объект, которого не существуют, попробуйте еще раз",
                                 reply_markup=params_kbd(param_name="building", data=available_buildings))
            await state.set_state(OrderForm.GET_BUILDING)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_SYSTEM)
async def process_getting_system(message: types.Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        available_systems = state_data["available_systems"]
        await message.answer(f"Название системы: {message.text}")
        if message.text in [system["system_name"] for system in available_systems]:
            system_id = [system for system in available_systems if system["system_name"] == message.text][0]["id"]
            await state.update_data(system_id=system_id)
            access_token = await get_value(f'{message.from_user.id}:access_token')
            _, available_important = await get_data_by_param(access_token=access_token, param="important")
            await state.update_data(available_important=available_important)
            await message.answer('Выберете степень важности',
                                 reply_markup=params_kbd(param_name="important", data=available_important))
            await state.set_state(OrderForm.GET_IMPORTANT)
        else:
            await message.answer("Вы выбрали систему, которой не существуют, попробуйте еще раз",
                                 reply_markup=params_kbd(param_name="system", data=available_systems))
            await state.set_state(OrderForm.GET_SYSTEM)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_IMPORTANT)
async def process_getting_important(message: types.Message, state: FSMContext) -> None:
    try:
        state_data = await state.get_data()
        available_important = state_data["available_important"]
        await message.answer(f"Cтепень важности: {message.text}")
        if message.text in [important["important_name"] for important in available_important]:
            important_id = \
                [important for important in available_important if important["important_name"] == message.text][0]["id"]
            await state.update_data(important_id=important_id)
            await message.answer('Укажите название материала', reply_markup=cancel_kbd())
            await state.update_data(materials=[])
            await state.set_state(OrderForm.GET_MATERIAL_NAME)
        else:
            await message.answer("Вы выбрали степень важности, которой не существуют, попробуйте еще раз",
                                 reply_markup=params_kbd(param_name="important", data=available_important))
            await state.set_state(OrderForm.GET_IMPORTANT)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_MATERIAL_NAME)
async def process_getting_material_name(message: types.Message, state: FSMContext) -> None:
    try:
        await message.answer(f'Название материала: {message.text}')
        await state.update_data(material_name=message.text)
        await message.answer('Укажите количество материала', reply_markup=cancel_kbd())
        await state.set_state(OrderForm.GET_MATERIAL_QUANTITY)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_MATERIAL_QUANTITY)
async def process_getting_material_quantity(message: types.Message, state: FSMContext) -> None:
    try:
        await message.answer(f'Количество материала: {message.text}')
        await state.update_data(material_quantity=message.text)
        state_data = await state.get_data()
        materials = state_data["materials"]
        material_name = state_data["material_name"]
        material_quantity = state_data["material_quantity"]
        if materials:
            materials = materials.append({"material": material_name,
                                          "quantity": material_quantity
                                          })
        else:
            materials = [{"material": material_name,
                          "quantity": material_quantity
                          }]
        await state.update_data(materials=materials)
        await message.answer('Хотите добавить еще?', reply_markup=more_material_kbd())
        await state.set_state(OrderForm.GET_MATERIAL_MORE)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_MATERIAL_MORE)
async def process_getting_material_more(message: types.Message, state: FSMContext) -> None:
    try:
        if message.text == "Да":
            await message.answer('Укажите название материала', reply_markup=cancel_kbd())
            await state.set_state(OrderForm.GET_MATERIAL_NAME)
        elif message.text == "Нет":
            await message.answer("Материалы добавлены")
            await message.answer("Добавьте примечания, если необходимо,\n"
                                 "если нет, то выберете кнопку 'Без примечаний'", reply_markup=no_description_kbd())
            await state.set_state(OrderForm.GET_DESCRIPTION)
        else:
            await message.answer("Пожауйлста, выберете из двух вариантов ответов", reply_markup=more_material_kbd())
            await state.set_state(OrderForm.GET_MATERIAL_MORE)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_DESCRIPTION)
async def process_getting_order_name(message: types.Message, state: FSMContext) -> None:
    try:
        if message.text == "Без примечаний":
            await message.answer("Без примечаний")
            await state.update_data(description=None)
        else:
            await message.answer(f"Примечаний: {message.text}")
            await state.update_data(description=message.text)
        access_token = await get_value(f'{message.from_user.id}:access_token')
        _, available_statuses = await get_data_by_param(access_token=access_token, param="status")
        await state.update_data(available_statuses=available_statuses)
        await message.answer('Выберете статус',
                             reply_markup=params_kbd(param_name="status", data=available_statuses))
        await state.set_state(OrderForm.GET_STATUS)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()


@order_router.message(OrderForm.GET_STATUS)
async def process_getting_status(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            state_data = await state.get_data()
            available_statuses = state_data["available_statuses"]
            await message.answer(f"Статус: {message.text}")
            if message.text in [status["status_name"] for status in available_statuses]:
                status_id = [status for status in available_statuses if status["status_name"] == message.text][0]["id"]
                await state.update_data(status_id=status_id)
                state_data = await state.get_data()
                if state_data["materials"]:
                    materials = state_data["materials"]
                else:
                    materials = []

                access_token = await get_value(f'{message.from_user.id}:access_token')
                status_code = await create_order_(access_token=access_token.decode(),
                                                  order_name=state_data["order_name"],
                                                  building_id=state_data["building_id"],
                                                  system_id=state_data["system_id"],
                                                  important_id=state_data["important_id"],
                                                  materials=materials,
                                                  creator_id=state_data["creator_id"],
                                                  description=state_data["description"],
                                                  status_id=state_data["status_id"])
                if status_code == 201:
                    await message.answer("Заявка успешно создана!", reply_markup=order_menu_kbd())
                else:
                    await message.answer("Во время создания заявки произошла ошибка", reply_markup=order_menu_kbd())
                    await state.clear()
            else:
                await message.answer("Вы выбрали статус, которого не существуют, попробуйте еще раз",
                                     reply_markup=params_kbd(param_name="status", data=available_statuses))
                await state.set_state(OrderForm.GET_STATUS)
    except Exception as err:
        print(err)
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=cancel_kbd())
        await state.clear()
