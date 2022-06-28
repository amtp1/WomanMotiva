import asyncio
from re import A

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from objects.globals import config
from objects import globals
from utils.utils import check_notices_polling


async def main():
    globals.bot = Bot(token=config.token, parse_mode="HTML")
    globals.dp = Dispatcher(globals.bot, storage=MemoryStorage())

    bot_info: dict = await globals.bot.get_me()
    logger.info(F"Bot username: @{bot_info.username}, Bot ID: {bot_info.id}")

    import commands

    try:
        asyncio.create_task(check_notices_polling())
    except Exception as e:
        logger.error(e)

    await globals.dp.start_polling()

if __name__ == "__main__":
    try:
        main_loop = asyncio.get_event_loop()
        main_loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
