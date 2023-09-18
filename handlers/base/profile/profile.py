from aiogram import types, Router, F, Bot
from aiogram.client.session import aiohttp
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiohttp import ClientConnectorError

from api.auth.authentication import decode_code
from api.base.user import get_user_data, update_password
from db.misc import get_value, delete_value
from handlers.base.profile.steps_change_password import ChangePasswordForm
from keyboards.base.profile import profile_services_kbd
from keyboards.menu import services_kbd, menu_kbd, cancel_kbd
from utils.auth import check_auth

from utils.user import format_user_data

profile_router = Router()


@profile_router.message(Command(commands=['profile']))
async def profile(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await message.answer('Профиль')
            await message.answer("Выберете раздел", reply_markup=profile_services_kbd())
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@profile_router.message(Command(commands=['user-info']))
async def user_info(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            access_token = await get_value(f'{message.from_user.id}:access_token')
            status_code, user_id = await decode_code(access_token=access_token.decode())
            status_code, user_data = await get_user_data(access_token=access_token.decode(), user_id=user_id)
            await message.answer('Данные пользователя')
            format_data = format_user_data(user_data=user_data)
            await message.answer(format_data, reply_markup=profile_services_kbd())
    except ClientConnectorError:
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@profile_router.message(Command(commands=['logout']))
async def logout(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await delete_value(f'{message.from_user.id}:access_token')
            await message.answer("Выход из учетной записи")
            await message.answer('Вы успешно вышли из системы', reply_markup=menu_kbd())
    except ClientConnectorError:
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@profile_router.message(Command(commands=['change-password']))
async def change_password(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await message.answer("Сменить пароль")
            await message.answer('Введите текущий пароль', reply_markup=cancel_kbd())
            await state.set_state(ChangePasswordForm.GET_DURING_PASSWORD)
    except ClientConnectorError:
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@profile_router.message(ChangePasswordForm.GET_DURING_PASSWORD)
async def process_getting_during_password(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await state.update_data(during_password=message.text)
            await message.delete()
            await message.answer(f"Новый пароль должен солдержать минимум 5 симоволов")
            await message.answer('Введите новый пароль', reply_markup=cancel_kbd())
            await state.set_state(ChangePasswordForm.GET_NEW_PASSWORD)
    except (Exception, ClientConnectorError):
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()


@profile_router.message(ChangePasswordForm.GET_NEW_PASSWORD)
async def process_get_new_password(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            access_token = await get_value(f'{message.from_user.id}:access_token')
            status_code, user_id = await decode_code(access_token=access_token.decode())
            await state.update_data(new_password=message.text)
            await message.delete()
            state_data = await state.get_data()
            during_password = state_data["during_password"]
            new_password = state_data["new_password"]
            status_code = await update_password(access_token=access_token.decode(),
                                                user_id=user_id,
                                                password=during_password,
                                                new_password=new_password)
            if status_code == 200:
                await message.answer('Вы успешно изменили пароль', reply_markup=profile_services_kbd())
            elif status_code == 401:
                await message.answer('Введен неправильный текуший пароль, попробуйте еще раз', reply_markup=cancel_kbd())
                await message.answer('Введите текущий пароль', reply_markup=cancel_kbd())
                await state.set_state(ChangePasswordForm.GET_DURING_PASSWORD)
            elif status_code == 422:
                await message.answer('Новый пароль должен содержать минимум 5 символов, попробуйте еще раз',
                                     reply_markup=cancel_kbd())
                await state.set_state(ChangePasswordForm.GET_NEW_PASSWORD)
            else:
                await message.answer('Неизвестная ошибка, сервис не работает', reply_markup=profile_services_kbd())
                await state.clear()
    except ClientConnectorError:
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
