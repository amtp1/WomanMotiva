from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.storage import FSMContext


from objects.globals import dp


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
