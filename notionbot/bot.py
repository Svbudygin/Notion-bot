import json
from calendar import Calendar
from datetime import date, datetime
# from aiogram.types import *
from aiogram import Bot, Dispatcher, executor, types
from config import TG_token, filename2
from main import test_function, answer_deadline_filter
from parse import connectin_check_time

# from testcalend import calendar_handler, months
months = ['Январь', "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
bot = Bot(TG_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def info(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton('Days', callback_data='Days')
    btm2 = types.InlineKeyboardButton('Weeks', callback_data='Weeks')
    btm3 = types.InlineKeyboardButton('Months', callback_data='Months')
    markup.add(btm1, btm2, btm3)
    await message.answer('Check the deadlines:', reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data in ['Days', 'Weeks', 'Months'])
async def process_day(callback_query):
    markup = types.InlineKeyboardMarkup()

    if callback_query.data == 'Days':
        btm1 = types.InlineKeyboardButton('1 day', callback_data='1d')
        btm2 = types.InlineKeyboardButton('2 days', callback_data='2d')
        btm3 = types.InlineKeyboardButton('3 days', callback_data='3d')
        btm4 = types.InlineKeyboardButton('4 days', callback_data='4d')
        btm5 = types.InlineKeyboardButton('5 days', callback_data='5d')
        btm6 = types.InlineKeyboardButton('6 days', callback_data='6d')
        markup.add(btm1, btm2, btm3, btm4, btm5, btm6)

    elif callback_query.data == 'Weeks':
        btm1 = types.InlineKeyboardButton('1 week', callback_data='1w')
        btm2 = types.InlineKeyboardButton('2 weeks', callback_data='2w')
        btm3 = types.InlineKeyboardButton('3 weeks', callback_data='3w')
        markup.add(btm1, btm2, btm3)

    elif callback_query.data == 'Months':
        btm1 = types.InlineKeyboardButton('1 month', callback_data='1m')
        btm2 = types.InlineKeyboardButton('2 months', callback_data='2m')
        markup.add(btm1, btm2)

    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f'Choose number of {callback_query.data}:', reply_markup=markup)


@dp.callback_query_handler()
async def callback(call):
    connectin_check_time(dict(call).get('from').get('id'))
    all_dd = test_function(answer_deadline_filter(call.data, filename2))
    for dd in all_dd:
        await call.message.answer(dd)


@dp.message_handler(commands=['calendar'])
async def show_calendar(message, handled_date=None):
    today = date.today()

    # dates = dict()
    # posts = get_posts(create_session())
    #
    # for post in posts:
    #     post_date = post.Date
    #
    #     if dates.get(post_date) is None:
    #         dates[post_date] = 0
    #
    #     dates[post_date] += 1
    #
    # if handled_date is not None:
    #     today = handled_date

    calendar = Calendar()
    weeks = calendar.monthdays2calendar(today.year, today.month)

    markup = types.InlineKeyboardMarkup(row_width=8)
    previous = types.InlineKeyboardButton(text="<-----------", callback_data='Пн')
    next = types.InlineKeyboardButton(text="----------->", callback_data='Пн')

    # previous.onClick(turn_calendar_page, today, -1)
    # next.onClick(turn_calendar_page, today, 1)

    markup.row(previous, next)

    monday_ = types.InlineKeyboardButton(text="Пн", callback_data='Пн')
    tuesday_ = types.InlineKeyboardButton(text="Вт", callback_data='Пн')
    wednesday_ = types.InlineKeyboardButton(text="Ср", callback_data='Пн')
    thursday_ = types.InlineKeyboardButton(text="Чт", callback_data='Пн')
    friday_ = types.InlineKeyboardButton(text="Пт", callback_data='Пн')
    saturday_ = types.InlineKeyboardButton(text="Сб", callback_data='Пн')
    sunday_ = types.InlineKeyboardButton(text="Вс", callback_data='Пн')

    markup.row(monday_, tuesday_, wednesday_,
               thursday_, friday_, saturday_, sunday_)

    for week in weeks:
        markup_row_ = list()
        for day in week:
            number = day[0]
            button = types.InlineKeyboardButton(str(number), callback_data=str(number))
            # button.width = button_width
            # button.onClick(calendar_handler, formatted_date, '(' in number)
            markup_row_.append(button)
        markup.row(*markup_row_)
    await message.answer(f"Выбранная дата: {months[today.month - 1]} {today.year} Года"
                         , reply_markup=markup)


executor.start_polling(dp)
