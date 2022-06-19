import re
from os import mkdir
from pathlib import Path

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from objects.globals import dp
from utils.api.api import API
from config.config import Config


TEMP_PATH = rF"{Path(__file__).resolve().parent.parent.parent}/temp"
TEMP_COUNTRIES = {
    "price": {
        "South Korea": "5000-10000",
        "Russia": "2800-7000",
        "Kazakhstan": "1800-6000",
        "Kyrgyzstan": "2300-3000",
        "Turkey": "3000-4000"
    },
    "inducement": {
        "South Korea": "Южной Корее",
        "Russia": "России",
        "Kazakhstan": "Казахстане",
        "Kyrgyzstan": "Кыргызстане",
        "Turkey": "Турции"
    }
}

config = Config()
api = API()


@dp.message_handler(lambda message: message.text == "O Motiva")
async def about(message: Message):
    about_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="О Motiva", callback_data="about_motiva")],
        [InlineKeyboardButton(text="Часто задаваемые вопросы",
                              callback_data="questions_motiva")],
        [InlineKeyboardButton(
            text="Сравнение стоимости операции", callback_data="diff_operation_price")]
    ])
    return await message.answer("Разделы", reply_markup=about_markup)


@dp.callback_query_handler(lambda query: query.data == "about_motiva")
async def about_motivia(query: CallbackQuery):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="О компании", callback_data="about_company")],
        [InlineKeyboardButton(text="О продукции",
                              callback_data="about_products")]
    ])
    return await query.message.edit_text(text="Разделы O Motiva", reply_markup=reply_markup)


@dp.callback_query_handler(lambda query: query.data == "about_company")
async def about_company(query: CallbackQuery):
    if not Path(TEMP_PATH).exists():
        mkdir(TEMP_PATH)
        with open(rF"{TEMP_PATH}/about.txt", "w") as f:
            f.close()

    with open(rF"{TEMP_PATH}/about.txt", "r", encoding="utf-8") as f:
        about_page = f.read()

    if not about_page:
        return await query.message.edit_text("Ничего не найдено")
    return await query.message.edit_text(about_page)


@dp.callback_query_handler(lambda query: query.data == "about_products")
async def about_products(query: CallbackQuery):
    if not Path(TEMP_PATH).exists():
        mkdir(TEMP_PATH)
        with open(rF"{TEMP_PATH}/products.txt", "w") as f:
            f.close()

    with open(rF"{TEMP_PATH}/products.txt", "r", encoding="utf-8") as f:
        about_page = f.read()

    if not about_page:
        return await query.message.edit_text("Ничего не найдено")
    return await query.message.edit_text(about_page)


@dp.callback_query_handler(lambda query: query.data == "questions_motiva")
async def questions_motivia(query: CallbackQuery):
    questions = api.get_questions()['questions']
    await query.message.edit_text("Часто задаваемые вопросы")
    for k, question in enumerate(questions):
        question_page = (F"<b>Вопрос#{k+1}</b>: {question['question']}\n"
                         F"<b>Ответ</b>: {question['answer']}")
        await query.message.answer(question_page)


@dp.callback_query_handler(lambda query: query.data == "diff_operation_price")
async def diff_operation_price(query: CallbackQuery):
    diff_page = ("В данном разделе приведен сравнительный анализ средних стоимостей операций в разных странах.\n"
                 "В стоимость не включены дополнительные расходы (билеты, гостиница, пребывание в стационаре, анализы). Указана только стоимость операции.\n"
                 "Нажмите на название страны что бы увидеть стоимость👇")
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Южная корея",
                              callback_data="country#South Korea")],
        [InlineKeyboardButton(text="Россия", callback_data="country#Russia")],
        [InlineKeyboardButton(
            text="Казахстан", callback_data="country#Kazakhstan")],
        [InlineKeyboardButton(
            text="Кыргызстан", callback_data="country#Kyrgyzstan")],
        [InlineKeyboardButton(text="Турция", callback_data="country#Turkey")],
    ])
    return await query.message.edit_text(diff_page, reply_markup=reply_markup)


@dp.callback_query_handler(lambda query: query.data.startswith(("country")))
async def select_country(query: CallbackQuery):
    country = re.sub("country#", "", query.data)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="go_back")]
    ])
    return await query.message.edit_text(F"Стоимость операции в {TEMP_COUNTRIES['inducement'][country]} ${TEMP_COUNTRIES['price'][country]}",
                                         reply_markup=reply_markup)


@dp.callback_query_handler(lambda query: query.data == "go_back")
async def select_country(query: CallbackQuery):
    return await diff_operation_price(query)
