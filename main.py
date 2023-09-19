import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from core.config import settings
from handlers import register_user_handlers, bot_commands
from handlers.base.menu import menu_router
from handlers.auth.authentication import auth_router
from handlers.base.ordering.order import order_router
from handlers.base.profile.profile import profile_router
from db.misc import redis


async def main():
    # Объект бота
    dp = Dispatcher(storage=RedisStorage(redis))
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    # Диспетчер
    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands_for_bot)

    register_user_handlers(dp)
    dp.include_router(auth_router)
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(order_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s"
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info('Bot stopped')
