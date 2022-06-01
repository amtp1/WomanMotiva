from os import mkdir
from pathlib import Path

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from objects.globals import dp
from utils.api.api import API
from config.config import Config


ABOUT_PATH = rF"{Path(__file__).resolve().parent.parent.parent}/temp"

config = Config()
api = API()


@dp.message_handler(lambda message: message.text == "O Motiva")
async def about(message: Message):
    about_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="О Motiva", callback_data="about_motiva")],
        [InlineKeyboardButton(text="Новости", callback_data="news_motiva")],
        [InlineKeyboardButton(text="Часто задаваемые вопросы", callback_data="questions_motiva")],
        [InlineKeyboardButton(text="Сравнение стоимости операции", callback_data="diff_operation_price")]
    ])
    return await message.answer("Разделы", reply_markup=about_markup)

@dp.callback_query_handler(lambda query: query.data == "about_motiva")
async def about_motivia(query: CallbackQuery):
    if not Path(ABOUT_PATH).exists():
        mkdir(ABOUT_PATH)
        with open(rF"{ABOUT_PATH}/about.txt", "w") as f:
            f.close()

    with open(rF"{ABOUT_PATH}/about.txt", "r", encoding="utf-8") as f:
        about_page = f.read()
    
    if not about_page:
        return await query.message.edit_text("Ничего не найдено")
    return await query.message.edit_text(about_page)

@dp.callback_query_handler(lambda query: query.data == "news_motiva")
async def news_motivia(query: CallbackQuery):
    pass

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
    diff_page = ("В данном разделе приведен сравнительный анализ стоимостей операций в разных странах.\n"
                "— Южная Корея $5000-10000\n"
                "— Россия $2800-7000\n"
                "— Казахстан $1800-6000\n"
                "— Кыргызстан $2300-3000\n"
                "— Турция $3000-4000\n"

                "<b>По курсу на 06.05.2022 (427.80)</b>\n"
                "<b>В стоимость не включены дополнительные расходы (билеты, гостиница, пребывание в стационаре, анализы). Указана только стоимость операции.</b>")
    return await query.message.edit_text(diff_page)