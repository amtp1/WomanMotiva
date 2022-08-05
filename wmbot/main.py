import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger
from clepsydra import create_async_scheduler, SingleRun, Context

from objects.globals import config
from objects import globals
from utils.utils import check_notices_polling, qrcode_check_notices_polling


scheduler = create_async_scheduler()


@scheduler.task
async def check_notices(context: Context):
    # asyncio.create_task(check_notices_polling())
    await check_notices_polling()


@scheduler.task
async def check_qrcode_notices(context: Context):
    await qrcode_check_notices_polling()


@scheduler.task
async def run_bot(context: Context):
    await globals.dp.start_polling()


async def main():
    globals.bot = Bot(token=config.token, parse_mode="HTML")
    globals.dp = Dispatcher(globals.bot, storage=MemoryStorage())

    bot_info: dict = await globals.bot.get_me()
    logger.info(F"Bot username: @{bot_info.username}, Bot ID: {bot_info.id}")

    import commands

    await scheduler.add_job("check_notices", rule=SingleRun(datetime.now()))
    await scheduler.add_job("check_qrcode_notices", rule=SingleRun(datetime.now()))
    await scheduler.add_job("run_bot", rule=SingleRun(datetime.now()))
    await scheduler.run()

if __name__ == "__main__":
    try:
        main_loop = asyncio.get_event_loop()
        main_loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
