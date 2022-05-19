from aiogram.dispatcher.filters.state import StatesGroup, State

class Deal(StatesGroup):
    city = State()