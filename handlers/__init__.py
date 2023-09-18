from aiogram import F
from aiogram import Router
from aiogram.filters.command import Command

from handlers.base.ordering.order import user_orders, order_menu, create_order
from handlers.help_commands import help_bot
from handlers.base.menu import menu_bot
from handlers.auth.authentication import start
from handlers.base.profile.profile import profile, logout, change_password, user_info

bot_commands = (
    ('start', 'Начало работы с ботом'),
    ('menu', 'Меню бота'),
    ('help', 'Помощь с ботом'),
    ('profile', 'Профиль пользователя'),
    ('logout', 'Выйти из учетнйо записи'),
)


def register_user_handlers(router: Router) -> None:
    """
    Зарегистрировать хендлеры пользователя
    :param router:
    """
    router.message.register(start, Command(commands=['start']))
    router.message.register(start, F.text == 'Старт')

    router.message.register(help_bot, Command(commands=['help']))
    router.message.register(help_bot, F.text == 'Помощь')

    router.message.register(menu_bot, Command(commands=['menu']))
    router.message.register(menu_bot, F.text == 'Меню')

    router.message.register(profile, Command(commands=['profile']))
    router.message.register(profile, F.text == 'Профиль')

    router.message.register(logout, Command(commands=['logout']))
    router.message.register(logout, F.text == 'Выйти из учетной записи')

    router.message.register(user_info, Command(commands=['user-info']))
    router.message.register(user_info, F.text == 'Данные пользователя')

    router.message.register(change_password, Command(commands=['change-password']))
    router.message.register(change_password, F.text == 'Сменить пароль')

    router.message.register(order_menu, Command(commands=['change-order_menu']))
    router.message.register(order_menu, F.text == 'Заявки')

    router.message.register(user_orders, Command(commands=['orders']))
    router.message.register(user_orders, F.text == 'Список заявок')

    router.message.register(create_order, Command(commands=['create_order']))
    router.message.register(create_order, F.text == 'Создать заявку')
