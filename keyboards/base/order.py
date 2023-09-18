from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def order_menu_kbd() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    order_menu_name = ["Создать заявку", "Список заявок"]
    for service in order_menu_name:
        keyboard_builder.row(types.KeyboardButton(text=service))
    keyboard_builder.row(types.KeyboardButton(text='Отмена'))
    return keyboard_builder.as_markup(resize_keyboard=True)


def params_kbd(param_name: str, data) -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    data_names = [dt[f"{param_name}_name"] for dt in data]
    for name in data_names:
        keyboard_builder.row(types.KeyboardButton(text=name))
    keyboard_builder.row(types.KeyboardButton(text='Отмена'))
    return keyboard_builder.as_markup(resize_keyboard=True)
