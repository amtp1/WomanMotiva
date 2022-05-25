from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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