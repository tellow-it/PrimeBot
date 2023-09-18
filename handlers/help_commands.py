from aiogram.types import Message

from keyboards.menu import menu_kbd


async def help_bot(message: Message):
    return await message.answer(
        'Добро пожаловать в бота. \n\n'
        f'С помощью данного бота вы можете:\n'
        f'\n - Создать заявку \n'
        f'\n - Изменить пароль \n'
        'Для регистрации напишите/выберете команду /start \n\n'
        'Для работы с ботом напишите/выберете команду /menu',
        reply_markup=menu_kbd()
    )
