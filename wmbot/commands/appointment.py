import re
import json
from datetime import datetime as dt

import requests
from io import BytesIO
from dateutil import parser
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.storage import FSMContext

from objects import globals
from objects.globals import dp
from states.states import Deal
from config.config import Config
from utils.api.api import API, WA_API
from my_calendar.calendar import DialogCalendar, valid_datetime, calendar_callback, Time

config = Config()
api = API()
wa_api = WA_API()

@dp.message_handler(lambda message: message.text == "Записаться на прием")
async def make_appointment(msg: Message):
    cities_inline_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Алматы", callback_data="city#Алматы"),
             InlineKeyboardButton(text="Нур-Султан", callback_data="city#Нур-Султан"),
             InlineKeyboardButton(text="Шымкент", callback_data="city#Шымкент")],

            [InlineKeyboardButton(text="Актобе", callback_data="city#Актобе"),
             InlineKeyboardButton(text="Караганда", callback_data="city#Караганда"),
             InlineKeyboardButton(text="Атырау", callback_data="city#Атырау")],

            [InlineKeyboardButton(text="Тараз", callback_data="city#Тараз"),
             InlineKeyboardButton(text="Павлодар", callback_data="city#Павлодар"),
             InlineKeyboardButton(text="Семей", callback_data="city#Семей")],

            [InlineKeyboardButton(text="Усть-Каменогорск", callback_data="city#Усть-Каменогорск"),
             InlineKeyboardButton(text="Кызылорда", callback_data="city#Кызылорда")]
        ]
    )

    return await msg.answer("Выберите город", reply_markup=cities_inline_markup)

@dp.callback_query_handler(lambda query: query.data.startswith(("city")))
async def select_city(query: CallbackQuery, state: FSMContext):
    city = re.sub("city#", "", query.data,)
    await state.update_data(city=city)

    contrain_select_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="contrain_yes"),
             InlineKeyboardButton(text="Нет", callback_data="contrain_no")],
        ]
    )
    return await query.message.edit_text(
        "Имеются ли у вас абсолютные противопоказания? Беременность, стадия кормления ребенка?",
        reply_markup=contrain_select_markup)

@dp.callback_query_handler(lambda query: query.data.startswith(("contrain")))
async def contrain_choose(query: CallbackQuery, state: FSMContext):
    is_contrain = re.sub("contrain_", "", query.data)
    is_contrain = True if is_contrain == "yes" else False
    if is_contrain:
        return await query.message.edit_text(
            "В этом случае мы не рекомендуем вам в ближайшее время проводить операцию. Пожалуйста проконсультируйтесь с нашими представителями по телефону:")
    else:
        await query.message.edit_text("Выберите хирурга")
        await state.update_data(is_contrain=is_contrain)

        data = await state.get_data()
        city = data.get("city")

        surgeons = api.get_surgeons(city=city)
        for surgeon in surgeons:
            globals.surgeons[surgeon["id"]] = surgeon["name"]
            id = surgeon["id"]
            name = surgeon["name"]
            city = surgeon["city"]
            wa_link = F"https://wa.me/{surgeon['wa_phone']}" if surgeon["wa_phone"] else "Отсутствует"
            image = read_image(surgeon["image"])
            choose_inline_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Выбрать", callback_data=rF"surgeon_{id}")]
                ]
            )
            await query.message.answer_photo(image, reply_markup=choose_inline_markup,
            caption=F"<b>Имя</b>: {name}\n"
                     F"<b>Город</b>: {city}\n"
                     F"<b>WhatsApp ссылка</b>: {wa_link}")

@dp.callback_query_handler(lambda query: query.data.startswith(("surgeon")))
async def select_surgeon(query: CallbackQuery, state: FSMContext):
    surgeon_id = re.sub("surgeon_", "", query.data)
    await state.update_data(surgeon_id=surgeon_id)
    await query.message.answer("Календарь", reply_markup=await DialogCalendar().start_calendar())

@dp.callback_query_handler(calendar_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer("Выберите интервал времени", reply_markup=await Time().start_time(date.strftime("%d-%m-%Y")))

@dp.callback_query_handler(lambda query: query.data.startswith(("int")))
async def time_interval(query: CallbackQuery, state: FSMContext):
    v_d = valid_datetime(query.data)
    await state.update_data(start_session=v_d[0], end_session=v_d[1])
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = KeyboardButton(text="Отправить телефон",
                                request_contact=True)
    keyboard.add(button_phone)
    await query.message.answer("Ваш номер телефона", reply_markup=keyboard)

@dp.message_handler(content_types=['contact'])
async def get_contact(message: Message, state: FSMContext):
    if message.contact is not None:
        remove_keyboard = ReplyKeyboardRemove()
        data = await state.get_data()
        surgeon_id = data.get("surgeon_id")
        city = data.get("city")
        start_session = data.get("start_session")
        end_session = data.get("end_session")
        phone = re.sub('[^0-9]', "", message.contact.phone_number)
        user_id = message.from_user.id
        surgeon_name = globals.surgeons[int(surgeon_id)]
        deal_response = api.create_deal(surgeon_id=surgeon_id, user_id=user_id,
            phone=phone, city=city,
            start_session=start_session, end_session=end_session)

        deal_id = deal_response["deal_id"]
        deal_created = deal_response["deal_created"]
        deal_created_str = dt.strftime(parser.parse(deal_created), "%d-%m-%Y %H:%M:%S")
        surgeon_message_text = (F"Заявка [#{deal_id}]\n"
                   F"Дата и время заявки: {deal_created_str}\n"
                   F"Начало консультации: {start_session}\n"
                   F"Конец консультации: {end_session}\n"
                   F"Телефон: {phone}")
        wa_api.send_message("79951060644", surgeon_message_text)

        complete_reg_page = (F"Вы успешно зарегистрированы на прием к хирургу Motiva:\n"
                             F"Начало консультации: {start_session}\n"
                             F"Конец консультации: {end_session}\n"
                             F"Хирург: {surgeon_name}\n"
                             F"Адрес: г.{city}\n"
                             F"Ниже вы видите QR код который нужно будет показать вашему хирургу непосредственно в день приема. Данный QR код дает специальный бонус от Motiva.")
        return await message.answer(complete_reg_page, reply_markup=remove_keyboard)

def read_image(image_path: str):
    response = requests.get(F"http://{config.host}:{config.port}{image_path}")
    img = BytesIO(response.content)
    return img