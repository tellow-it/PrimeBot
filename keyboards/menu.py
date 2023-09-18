from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def menu_kbd() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.row(types.KeyboardButton(text='Меню'))
    return keyboard_builder.as_markup(resize_keyboard=True)


def cancel_kbd() -> ReplyKeyboardMarkup:
    keyboard_build = ReplyKeyboardBuilder()
    keyboard_build.row(types.KeyboardButton(text='Отмена'))
    return keyboard_build.as_markup(resize_keyboard=True)


def services_kbd() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    services_name = ["Профиль", "Заявки"]
    for service in services_name:
        keyboard_builder.row(types.KeyboardButton(text=service))
    keyboard_builder.row(types.KeyboardButton(text='Отмена'))
    return keyboard_builder.as_markup(resize_keyboard=True)

