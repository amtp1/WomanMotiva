import re

import requests
from io import BytesIO
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from objects.globals import dp
from utils.api.api import API
from config.config import Config


config = Config()
api = API()


@dp.message_handler(lambda message: message.text == "O Motivia")
async def about(message: Message):
    about_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="О Motivia", callback_data="about_motivia")],
        [InlineKeyboardButton(text="Хирурги Motivia", callback_data="surgeons_motivia")],
        [InlineKeyboardButton(text="Новости", callback_data="news_motivia")],
        [InlineKeyboardButton(text="Часто задаваемые вопросы", callback_data="questions_motivia")]
    ])
    return await message.answer("Разделы", reply_markup=about_markup)

@dp.callback_query_handler(lambda query: query.data == "about_motivia")
async def about_motivia(query: CallbackQuery):
    pass

@dp.callback_query_handler(lambda query: query.data == "surgeons_motivia")
async def surgeons_motivia(query: CallbackQuery):
    cities_inline_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Алматы", callback_data="_city#Алматы"),
             InlineKeyboardButton(text="Нур-Султан", callback_data="_city#Нур-Султан"),
             InlineKeyboardButton(text="Шымкент", callback_data="_city#Шымкент")],

            [InlineKeyboardButton(text="Актобе", callback_data="_city#Актобе"),
             InlineKeyboardButton(text="Караганда", callback_data="_city#Караганда"),
             InlineKeyboardButton(text="Атырау", callback_data="_city#Атырау")],

            [InlineKeyboardButton(text="Тараз", callback_data="_city#Тараз"),
             InlineKeyboardButton(text="Павлодар", callback_data="_city#Павлодар"),
             InlineKeyboardButton(text="Семей", callback_data="_city#Семей")],

            [InlineKeyboardButton(text="Усть-Каменогорск", callback_data="_city#Усть-Каменогорск"),
             InlineKeyboardButton(text="Кызылорда", callback_data="_city#Кызылорда")]
        ]
    )

    return await query.message.edit_text("Выберите город", reply_markup=cities_inline_markup)

@dp.callback_query_handler(lambda query: query.data == "news_motivia")
async def news_motivia(query: CallbackQuery):
    pass

@dp.callback_query_handler(lambda query: query.data == "questions_motivia")
async def questions_motivia(query: CallbackQuery):
    pass

@dp.callback_query_handler(lambda query: query.data.startswith(("_city")))
async def contrain_choose(query: CallbackQuery):
    city = re.sub("_city#", "", query.data)
    await query.message.edit_text(F"Хирурги по городу {city}")
    surgeons = api.get_surgeons(city=city)
    for surgeon in surgeons:
        id = surgeon["id"]
        name = surgeon["name"]
        city = surgeon["city"]
        clinic = surgeon["clinic"]
        instagram_link = surgeon["instagram_link"] if surgeon["instagram_link"] else "Отсутствует"
        image = read_image(surgeon["image"])
        await query.message.answer_photo(image,
        caption=F"<b>Имя</b>: {name}\n"
                    F"<b>Город</b>: {city}\n"
                    F"<b>Клиника</b>: {clinic}\n"
                    F"Instagram: {instagram_link}")

def read_image(image_path: str):
    response = requests.get(F"http://{config.host}:{config.port}{image_path}")
    img = BytesIO(response.content)
    return img