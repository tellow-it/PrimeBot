from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def profile_services_kbd() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    profile_services_name = ["Данные пользователя", "Сменить пароль", "Выйти из учетной записи"]
    for service in profile_services_name:
        keyboard_builder.row(types.KeyboardButton(text=service))
    keyboard_builder.row(types.KeyboardButton(text='Отмена'))
    return keyboard_builder.as_markup(resize_keyboard=True)
