from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiohttp import ClientConnectorError
from handlers.auth.steps_auth import AuthForm
from aiogram.types import Message, ReplyKeyboardRemove
from db.misc import get_value, set_value
from keyboards.menu import cancel_kbd
from keyboards.menu import menu_kbd

from api.auth.authentication import login

auth_router = Router()


@auth_router.message(F.text == "Отмена")
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


@auth_router.message(Command(commands=['start']))
async def start(message: types.Message, state: FSMContext) -> None:
    await message.answer('Начало работы с ботом, проверка пользователя...', reply_markup=cancel_kbd())
    try:
        access_token = await get_value(f'{message.from_user.id}:access_token')
        if access_token:
            await message.answer('Вы уже авторизованы', reply_markup=menu_kbd())
        else:
            await message.answer(
                'Введите телефон, под которым вас зарегистрировал администратор',
                reply_markup=cancel_kbd())
            await state.set_state(AuthForm.GET_PHONE)
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в администратору',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@auth_router.message(AuthForm.GET_PHONE)
async def process_getting_telephone(message: types.Message, state: FSMContext) -> None:
    try:
        await message.answer(f"Ваш телефон: {message.text}")
        await state.update_data(telephone=message.text)
        await message.answer('Введите пароль', reply_markup=cancel_kbd())
        await state.set_state(AuthForm.GET_PASSWORD)
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@auth_router.message(AuthForm.GET_PASSWORD)
async def process_code(message: types.Message, state: FSMContext) -> None:
    try:
        await state.update_data(password=message.text)
        await message.delete()
        state_data = await state.get_data()
        telephone = state_data["telephone"]
        password = state_data["password"]
        status_code, access_token = await login(telephone=telephone, password=password)
        if status_code == 200:
            await set_value(f'{message.from_user.id}:access_token', access_token)
            await message.answer('Вы успешно авторизированы')
            await message.answer('Выберете раздел, который вас интересует', reply_markup=menu_kbd())
        elif status_code == 401:
            await message.answer('Неправильный пароль, попробуйте еще раз', reply_markup=cancel_kbd())
            await message.answer('Введите пароль', reply_markup=cancel_kbd())
            await state.set_state(AuthForm.GET_PASSWORD)
        elif status_code == 404:
            await message.answer('Пользователя с таким телефоном нет, попробуйте еще раз', reply_markup=cancel_kbd())
            await message.answer(
                'Введите телефон, под которым вас зарегистрировал администратор',
                reply_markup=cancel_kbd())
            await state.set_state(AuthForm.GET_PHONE)
        elif status_code == 422:
            await message.answer('Неправильный пароль, пароль должен содержать минимум 5 символов, попробуйте еще раз',
                                 reply_markup=cancel_kbd())
            await message.answer('Введите пароль', reply_markup=cancel_kbd())
            await state.set_state(AuthForm.GET_PASSWORD)
        else:
            await message.answer('Неизвестная ошибка, сервис не работает', reply_markup=menu_kbd())
            await state.clear()
    except ClientConnectorError:
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
