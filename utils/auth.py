from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message

from api.auth.authentication import decode_code
from api.base.user import get_user_data
from db.misc import get_value, delete_value


async def check_auth(message: Message, state: FSMContext) -> bool:
    access_token: bytes = await get_value(f'{message.from_user.id}:access_token')
    if access_token:
        status_code, user_id = await decode_code(access_token=access_token.decode())
        status_code, user_data = await get_user_data(access_token=access_token.decode(), user_id=user_id)
        if user_data:
            return True
        else:
            await message.answer(
                'Ваша учетная запись была удалена, обратитесь к администратору',
                reply_markup=ReplyKeyboardRemove())
            await state.clear()
            await delete_value(f'{message.from_user.id}:access_token')
            return False
    else:
        await message.answer(
            'Вы не авторизированы в системе.\n'
            'Пожалуйста, введите команду /start',
            reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return False
