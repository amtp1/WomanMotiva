import io
import pytz
import json
import aiohttp
from asyncio import sleep
from datetime import datetime as dt, timedelta

import requests
from loguru import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from objects import globals
from utils.api.api import API
from config.config import Config
from utils.api.api import WA_API

TIME_ZONE = pytz.timezone('Asia/Almaty')
TIME_ZONE_DELTA = timedelta(hours=5)
BEFORE_CHECK_QRCODE_NOTICES_SECONDS: int = 7200
BEFORE_CHECK_NOTICES_SECONDS: int = 3600

config: Config = Config()
api: API = API()
wa_api: WA_API = WA_API()


async def check_notices_polling():
    while True:
        notices: dict = api.get_notices()['notices']

        if notices:
            for notice in notices:
                is_bot = await check_bot(int(notice['user_id']))

                if not is_bot:
                    created_deal = dt.strptime(
                        notice['created'], "%Y-%m-%d %H:%M:%S") + TIME_ZONE_DELTA + timedelta(hours=int(config.timeout_sec))
                    current_datetime = dt.strptime(dt.now(TIME_ZONE).strftime(
                        "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

                    is_now = (created_deal - current_datetime).total_seconds()

                    if is_now <= BEFORE_CHECK_NOTICES_SECONDS:
                        api.change_notice_status(deal_id=notice['deal_id'])
                        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="Да", callback_data=F"notice_yes#{notice['deal_id']}"),
                             InlineKeyboardButton(text="Нет", callback_data=F"notice_no#{notice['deal_id']}")]
                        ])
                        await globals.bot.send_message(chat_id=notice['user_id'],
                                                       text=F"<b>Заявка#{notice['deal_id']}</b>\n"
                                                       F"Пожалуйста ответьте, связался ли с вами представитель хирурга к которому вы записались?",
                                                       reply_markup=reply_markup)

        await qrcode_check_notices_polling()
        await sleep(3)


async def qrcode_check_notices_polling():
    notices = api.get_qrcode_notices()['qrcode_notices']

    if notices:
        for notice in notices:
            is_bot = await check_bot(int(notice['user_id']))

            if not is_bot:
                end_session = dt.strptime(
                    notice['end_session'], "%Y-%m-%d %H:%M:%S") + TIME_ZONE_DELTA
                current_datetime = dt.strptime(dt.now(TIME_ZONE).strftime(
                    "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

                is_now = (end_session - current_datetime).total_seconds()

                if is_now <= BEFORE_CHECK_QRCODE_NOTICES_SECONDS:
                    api.change_qrcode_notice_status(deal_id=notice['deal_id'])
                    return await globals.bot.send_photo(chat_id=notice['user_id'], photo=read_qr_code_from_url(r"qrcode.png"),
                                                        caption=F"<b>Заявка#{notice['deal_id']}</b>\n"
                                                        F"Данный QR код который необходимо показать хирургу или администратору клиники при посещении.")


async def check_bot(user_id: int) -> bool:
    me = await globals.bot.get_me()
    return me.id == user_id


async def check_wa_token(accessToken):
    url = 'https://api.chatapp.online/v1/tokens/check'

    headers = {
        'Authorization': accessToken,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            body = await response.text()
            body = json.loads(body)
            if not body.get("success"):
                data = wa_api.auth().get("data")
                token = data.get("accessToken")
                config.change_value("WA_TOKEN", token)
                logger.info("Token regenerated!")

    await sleep(43200)


def cities_markup(cities: list, callback_data: str):
    inline_cities: list = []
    cities: list[list] = list(paginate(cities, 3))
    for city in cities:
        inline_cities.append([InlineKeyboardButton(
            text=c, callback_data=F"{callback_data}{c}") for c in city])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_cities)
    return markup


def paginate(data_list: list, count: int):
    for i in range(0, len(data_list), count):
        yield data_list[i:i + count]


def read_qr_code_from_url(image_name: str):
    response = requests.get(
        F"http://{config.host}:{config.port}/media/qrcode/{image_name}")
    img = io.BytesIO(response.content)
    return img
