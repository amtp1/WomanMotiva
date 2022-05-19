from aiogram import Dispatcher, Bot

from config.config import Config

config: Config = Config() # Init config object.

bot: Bot = None # Set bot object without initialize.
dp: Dispatcher = None # Set dispatcher object without initialize.


surgeons: dict = {}