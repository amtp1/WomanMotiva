from aiogram.dispatcher.filters.state import StatesGroup, State


class Deal(StatesGroup):
    fio = State()
    email = State()
