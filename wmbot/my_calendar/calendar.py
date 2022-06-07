import calendar
from datetime import datetime

from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData

# setting callback_data prefix and parts
calendar_callback = CallbackData('dialog_calendar', 'act', 'year', 'month', 'day')
ignore_callback = calendar_callback.new("IGNORE", -1, -1, -1)  # for buttons with no answer


class DialogCalendar:
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

    def __init__(self, year: int = datetime.now().year, month: int = datetime.now().month):
        self.year = year
        self.month = month

    async def start_calendar(
        self,
        year: int = datetime.now().year
    ) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=5)
        # first row - years
        inline_kb.row()
        for value in range(year, year + 2):
            inline_kb.insert(InlineKeyboardButton(
                value,
                callback_data=calendar_callback.new("SET-YEAR", value, -1, -1)
            ))
        # nav buttons
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            '<<',
            callback_data=calendar_callback.new("PREV-YEARS", year, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=calendar_callback.new("NEXT-YEARS", year, -1, -1)
        ))

        return inline_kb

    async def _get_month_kb(self, year: int):
        inline_kb = InlineKeyboardMarkup(row_width=6)
        # first row with year button
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(
            year,
            callback_data=calendar_callback.new("START", year, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        # two rows with 6 months buttons
        inline_kb.row()
        for month in self.months[0:6]:
            inline_kb.insert(InlineKeyboardButton(
                month,
                callback_data=calendar_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1)
            ))
        inline_kb.row()
        for month in self.months[6:12]:
            inline_kb.insert(InlineKeyboardButton(
                month,
                callback_data=calendar_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1)
            ))
        return inline_kb

    async def _get_days_kb(self, year: int, month: int):
        inline_kb = InlineKeyboardMarkup(row_width=7)
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            year,
            callback_data=calendar_callback.new("START", year, -1, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            self.months[month - 1],
            callback_data=calendar_callback.new("SET-YEAR", year, -1, -1)
        ))
        inline_kb.row()
        #for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        #    inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if(day == 0):
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("SET-DAY", year, month, day)
                ))
        return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        return_data = (False, None)
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        if data['act'] == "SET-YEAR":
            self.message = "Выберите месяц"
            await query.message.edit_reply_markup(await self._get_month_kb(int(data['year'])))
        if data['act'] == "PREV-YEARS":
            new_year = int(data['year']) - 5
            #await query.message.edit_reply_markup(await self.start_calendar(new_year))
        if data['act'] == "NEXT-YEARS":
            new_year = int(data['year']) + 5
            #await query.message.edit_reply_markup(await self.start_calendar(new_year))
        if data['act'] == "START":
            #self.message = "Выберите год"
            await query.message.edit_reply_markup(await self.start_calendar(int(data['year'])))
        if data['act'] == "SET-MONTH":
            if not self.valid_month(year=int(data["year"]), month=int(data["month"])):
                try:
                    await query.answer("Был выбран неверный месяц, попробуйте еше раз!")
                    await query.message.edit_reply_markup(await self._get_month_kb(int(data['year'])))
                except:
                    pass
            else:
                await query.message.edit_reply_markup(await self._get_days_kb(int(data['year']), int(data['month'])))
        if data['act'] == "SET-DAY":
            if not self.valid_day(year=int(data['year']), month=int(data['month']), day=int(data['day'])):
                try:
                    await query.answer("Был выбран неверный день, попробуйте еше раз!")
                    await query.message.edit_reply_markup(await self._get_days_kb(int(data['year']), int(data['month'])))
                except:
                    pass
            else:
                await query.message.delete_reply_markup()   # removing inline keyboard
                return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        return return_data

    def valid_month(self, year: int, month: int):
        current_year: int = int(datetime.now().year)
        current_month: int = int(datetime.now().month)

        if year == current_year and month < current_month:
            return False
        return True

    def valid_day(self, year: int, month: int, day: int):
        current_year: int = int(datetime.now().year)
        current_month: int = int(datetime.now().month)
        current_day: int = int(datetime.now().day)

        if year == current_year and month == current_month and day <= current_day:
            return False
        return True


class Time:
    intervals = []

    def __init__(self):
        pass

    async def start_time(
        self, date: str
    ) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
            [InlineKeyboardButton(text="09:00-10:00", callback_data=F"int_{date} 09:00-10:00"),
            InlineKeyboardButton(text="10:00-11:00", callback_data=F"int_{date} 10:00-11:00"),
            InlineKeyboardButton(text="11:00-12:00", callback_data=F"int_{date} 11:00-12:00")],

            [InlineKeyboardButton(text="12:00-13:00", callback_data=F"int_{date} 12:00-13:00"),
            InlineKeyboardButton(text="13:00-14:00", callback_data=F"int_{date} 13:00-14:00"),
            InlineKeyboardButton(text="14:00-15:00", callback_data=F"int_{date} 14:00-15:00")],

            [InlineKeyboardButton(text="15:00-16:00", callback_data=F"int_{date} 15:00-16:00"),
            InlineKeyboardButton(text="16:00-17:00", callback_data=F"int_{date} 16:00-17:00"),
            InlineKeyboardButton(text="17:00-18:00", callback_data=F"int_{date} 17:00-18:00")],

            [InlineKeyboardButton(text="18:00-19:00", callback_data=F"int_{date} 18:00-19:00")]
        ])

        return inline_kb


def valid_datetime(_datetime: str) -> tuple:
    suffix, _datetime = _datetime.split("_")
    dt = _datetime.split(" ")
    start_time, end_time = _datetime.split(" ")[1].split("-")
    s_dt = datetime.strptime(F"{dt[0]} {start_time}", "%d-%m-%Y %H:%M")
    e_dt = datetime.strptime(F"{dt[0]} {end_time}", "%d-%m-%Y %H:%M")
    return (s_dt, e_dt,)