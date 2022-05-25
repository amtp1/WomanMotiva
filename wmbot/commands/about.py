from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from objects.globals import dp

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
    pass

@dp.callback_query_handler(lambda query: query.data == "news_motivia")
async def news_motivia(query: CallbackQuery):
    pass

@dp.callback_query_handler(lambda query: query.data == "questions_motivia")
async def questions_motivia(query: CallbackQuery):
    pass