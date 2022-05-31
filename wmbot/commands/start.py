from datetime import datetime as dt
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.storage import FSMContext

from my_calendar.calendar import DialogCalendar, calendar_callback, Time, valid_datetime
#from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

from objects.globals import dp, bot


@dp.message_handler(commands="start")
async def start(msg: Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Записаться на прием"),
             KeyboardButton(text="O Motiva")]
        ])

    return await msg.answer(
        text=F"Здравствуйте {msg.from_user.first_name}, мы готовы помочь Вам с подбором имплантатов, клиники и врача.",
        reply_markup=markup)