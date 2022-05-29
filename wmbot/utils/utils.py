from asyncio import sleep
from datetime import datetime as dt

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.api.api import API
from objects import globals

api = API()

def cities_markup(cities: list, callback_data: str):
    inline_cities = []
    cities = list(paginate(cities, 3))
    for city in cities:
        inline_cities.append([InlineKeyboardButton(text=c, callback_data=F"{callback_data}{c}") for c in city])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_cities)
    return markup

def paginate(data_list: list, count: int):
    for i in range(0, len(data_list), count):
        yield data_list[i:i + count]

async def check_notices_polling():
    while True:
        notices = api.get_noticies()['notices']

        for notice in notices:
            end_session = dt.strptime(notice['end_session'], "%Y-%m-%d %H:%M:%S")
            current_datetime = dt.strptime(dt.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

            is_now = (end_session - current_datetime).total_seconds()

            if is_now < 0:
                api.change_notice_status(deal_id=notice['deal_id'])
                reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Да", callback_data=F"notice_yes#{notice['deal_id']}"),
                     InlineKeyboardButton(text="Нет", callback_data=F"notice_no#{notice['deal_id']}")]
                    ])
                await globals.bot.send_message(chat_id=notice['user_id'], text="Пожалуйста ответьте, связался ли с вами представитель хирурга к которому вы записались?",
                    reply_markup=reply_markup)

        await sleep(5)