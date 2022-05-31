import re
from datetime import datetime as dt
from asyncio import sleep

import requests
from io import BytesIO
from dateutil import parser
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.dispatcher.storage import FSMContext

from objects import globals
from objects.globals import dp
from states.states import Deal
from config.config import Config
from utils.api.api import API, WA_API
from my_calendar.calendar import DialogCalendar, valid_datetime, calendar_callback, Time
from utils.utils import cities_markup

config = Config() # Init Config object.
api = API() # Init API object.
wa_api = WA_API() # Init WA_API object.


@dp.message_handler(lambda message: message.text == "Записаться на прием")
async def make_appointment(message: Message, state: FSMContext):
    """The function creates a new deal. Get cities.

    Parameters
    ----------
        message : Message

    Returns
    -------
        answer : method of Message object
    """
    await state.update_data(user_id=message.from_user.id)
    cities = api.get_cities()["cities"]
    markup = cities_markup(cities, callback_data="city#")
    return await message.answer("Выберите город", reply_markup=markup)

@dp.callback_query_handler(lambda query: query.data.startswith(("city")))
async def select_city(query: CallbackQuery, state: FSMContext):
    """The function creates a new deal. Contrain choose. (YES/NO)

    Parameters
    ----------
        query : CallbackQuery

    Returns
    -------
        edit_text : method of Message object which is inherited from CallbackQuery
    """

    city = re.sub("city#", "", query.data,)
    await state.update_data(city=city)

    contrain_select_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="contrain_yes"),
             InlineKeyboardButton(text="Нет", callback_data="contrain_no")]
        ]
    )
    return await query.message.edit_text(
        "Имеются ли у вас абсолютные противопоказания? Беременность, период грудного вскармливания?",
        reply_markup=contrain_select_markup)

@dp.callback_query_handler(lambda query: query.data.startswith(("contrain")))
async def contrain_choose(query: CallbackQuery, state: FSMContext):
    """Contrain choose. (YES/NO)

    Parameters
    ----------
        query : CallbackQuery

    Returns
    -------
        edit_text : method of Message object which is inherited from CallbackQuery
    """

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
            globals.surgeons[surgeon["id"]] = (surgeon["name"], surgeon["wa_phone"],)
            id = surgeon["id"]
            name = surgeon["name"]
            city = surgeon["city"]
            clinic = surgeon["clinic"]
            address = surgeon["address"] if surgeon["address"] else "Отсутствует"
            instagram_link = surgeon["instagram_link"]
            image = read_image(surgeon["image"])
            choose_inline_markup = InlineKeyboardMarkup()
            if instagram_link:
                choose_inline_markup.add(InlineKeyboardButton(text="Instagram", url=instagram_link))
            choose_inline_markup.add(InlineKeyboardButton(text="Выбрать", callback_data=rF"surgeon_{id}"))
            await query.message.answer_photo(image, reply_markup=choose_inline_markup,
            caption=F"<b>Имя</b>: {name}\n"
                     F"<b>Город</b>: {city}\n"
                     F"<b>Клиника</b>: {clinic}\n"
                     F"<b>Адрес</b>: {address}")

@dp.callback_query_handler(lambda query: query.data.startswith(("surgeon")))
async def select_surgeon(query: CallbackQuery, state: FSMContext):
    """The function send calendar. Default month: now

    Parameters
    ----------
        query : CallbackQuery
        state : FSMContext

    Returns
    -------
        answer : method of Message object which is inherited from CallbackQuery
    """

    surgeon_id = re.sub("surgeon_", "", query.data)
    await state.update_data(surgeon_id=surgeon_id)
    await query.message.answer("Календарь", reply_markup=await DialogCalendar().start_calendar())

@dp.callback_query_handler(calendar_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    """The function select calendar parts.

    Parameters
    ----------
        query : CallbackQuery
        callback_data : dict
        state : FSMContext

    Returns
    -------
        answer : method of Message object which is inherited from CallbackQuery
    """

    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date=date.strftime("%d-%m-%Y"))
        await callback_query.message.answer("Выберите интервал времени", reply_markup=await Time().start_time(date.strftime("%d-%m-%Y")))

@dp.callback_query_handler(lambda query: query.data.startswith(("int")))
async def time_interval(query: CallbackQuery, state: FSMContext):
    """The function select calendar parts.

    Parameters
    ----------
        query : CallbackQuery
        state : FSMContext

    Returns
    -------
        answer : method of Message object which is inherited from CallbackQuery
    """

    await state.update_data(time=query.data.split(" ")[1])
    v_d = valid_datetime(query.data)
    await state.update_data(start_session=v_d[0], end_session=v_d[1])
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = KeyboardButton(text="Отправить телефон",
                                request_contact=True)
    keyboard.add(button_phone)
    await query.message.answer('Нажмите кнопку "отправить телефон" 🙂⬇️⬇️⬇️', reply_markup=keyboard)

@dp.message_handler(content_types=['contact'])
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(phone=re.sub('[^0-9]', "", message.contact.phone_number))
    remove_keyboard = ReplyKeyboardRemove()
    await message.answer("Ваше ФИО\n/skip - Пропустить", reply_markup=remove_keyboard)
    await Deal.fio.set()

@dp.message_handler(state=Deal.fio)
async def get_fio(message: Message, state: FSMContext):
    if message.text != "/skip":
        await state.update_data(fio=message.text)
    await message.answer("Ваш email\n/skip - Пропустить")
    await Deal.email.set()

@dp.message_handler(state=Deal.email)
async def get_email(message: Message, state: FSMContext):
    if message.text != "/skip":
        await state.update_data(email=message.text)

    consultation_format_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Онлайн", callback_data="cons#online"),
         InlineKeyboardButton(text="Оффлайн", callback_data="cons#offline")]
    ])
    globals.data = await state.get_data()
    await state.finish()
    return await message.answer("Выберите предпочтительный формат проведения консультации", reply_markup=consultation_format_markup)

@dp.callback_query_handler(lambda query: query.data.startswith(("cons")))
async def consultation_format(query: CallbackQuery, state: FSMContext):
    data = globals.data

    user_id = data.get("user_id")
    surgeon_id = data.get("surgeon_id")
    phone = data.get("phone")
    city = data.get("city")
    fio = data.get("fio")
    email = data.get("email")
    date = data.get("date")
    time = data.get("time")
    cons_format = re.sub("cons#", "", query.data)
    start_session = data.get("start_session")
    end_session = data.get("end_session")
    state_surgeon_data = globals.surgeons[int(surgeon_id)]
    surgeon_name = state_surgeon_data[0]
    surgeon_wa_phone = state_surgeon_data[1]
    deal_response = api.create_deal(surgeon_id=surgeon_id, user_id=user_id,
        phone=phone, city=city, fio=fio, email=email, cons_format=cons_format,
        start_session=start_session, end_session=end_session)

    deal_id = deal_response["deal_id"]
    deal_created = deal_response["deal_created"]
    code = deal_response["code"]
    deal_created_str = dt.strftime(parser.parse(deal_created), "%d-%m-%Y %H:%M:%S")
    surgeon_message_text = (F"Заявка [#{deal_id}]\n"
                F"ФИО: {fio}\n"
                F"Дата и время заявки: {deal_created_str}\n"
                F"Дата консультации: {date}\n"
                F"Время консультации: {time}\n"
                F"Телефон: {phone}\n"
                F"Код: {code}")
    wa_api.send_message(surgeon_wa_phone, surgeon_message_text)

    new_deal_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать сначала", callback_data="new_deal")]
    ])

    complete_reg_page = (F"Вы успешно зарегистрированы на прием к хирургу Motiva:\n"
                         F"Дата консультации: {date}\n"
                         F"Время консультации: {time}\n"
                         F"Хирург: {surgeon_name}\n"
                         F"Адрес: г.{city}")
    await query.message.answer(complete_reg_page, reply_markup=new_deal_markup)
    # await query.message.answer_photo(read_qr_code_from_url(r"qrcode.png"))
    # await message.answer_photo(read_qr_code_from_path(r"qr_code/qrcode.png"))
    await notify_about_deal(query.message, deal_id)

@dp.callback_query_handler(lambda query: query.data.startswith(("new_deal")))
async def new_deal(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Новая заявка")
    return await make_appointment(query.message, state)

@dp.callback_query_handler(lambda query: query.data.startswith(("notice")))
async def notice_request(query: CallbackQuery):
    deal_id = re.sub("[notice_yes# notice_no#]", "", query.data)
    answer = re.sub("[#, _]", "", query.data.replace("notice", "").replace(deal_id, ""))

    if answer == "yes":
        api.change_status(deal_id=deal_id, status="confirmed")
        return await query.message.edit_text("Спасибо за ваш ответ!")
    elif answer == "no":
        api.change_status(deal_id=deal_id, status="unconfirmed")
        return await query.message.edit_text("Спасибо за ваш ответ, мы уточним у хирурга статус вашей записи и попросим подтвердить ее.")

async def notify_about_deal(message: Message, deal_id: int):
    await sleep(int(config.timeout_sec))
    inline_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data=F"communicate#yes_{deal_id}"),
             InlineKeyboardButton(text="Нет", callback_data=F"communicate#no_{deal_id}")]
        ]
    )
    await message.answer(
        "Пожалуйста ответьте, связался ли с вами представитель хирурга к которому вы записались?",
        reply_markup=inline_markup)

def read_image(image_path: str):
    response = requests.get(F"http://{config.host}:{config.port}{image_path}")
    img = BytesIO(response.content)
    return img

def read_qr_code_from_url(image_name: str):
    response = requests.get(F"http://{config.host}:{config.port}/media/qrcode/{image_name}")
    img = BytesIO(response.content)
    return img

def read_qr_code_from_path(image_path: str):
    with open(image_path, "rb") as img:
        img = img.read()
    return img