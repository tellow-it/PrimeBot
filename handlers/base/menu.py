from aiogram import types, Router, F, Bot
from aiogram.client.session import aiohttp
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiohttp import ClientConnectorError

import base64

from keyboards.menu import services_kbd
from utils.auth import check_auth

menu_router = Router()


@menu_router.message(Command(commands=['menu']))
async def menu_bot(message: types.Message, state: FSMContext) -> None:
    try:
        result_check = await check_auth(message, state)
        if result_check:
            await message.answer('Меню бота')
            await message.answer('Выберите пункт', reply_markup=services_kbd())
    except ClientConnectorError:
        await message.answer('К сожалению сервис недоступен, пожалуйста, сообщите в поддержку',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
