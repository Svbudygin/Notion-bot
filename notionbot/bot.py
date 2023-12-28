import sqlite3
import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from calendar import Calendar
from datetime import date, datetime
from aiogram import Bot, Dispatcher, executor, types
from dateutil.relativedelta import relativedelta
from config import TG_token
from main import test_function, answer_deadline_filter
from parse import connectin_check_time, get_data_from_json_for_calendar, Mistake, create_page

months = ['Январь', "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
bot = Bot(TG_token)
dp = Dispatcher(bot, storage=MemoryStorage())

message_delete = {}


class Form(StatesGroup):
    waiting_database_token = State()
    waiting_token = State()
    add_title = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("data/tokens.sql")
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS tokens_tbl (id int auto_increment primary key, userid varchar(200), NotionToken varchar(200), DBToken varchar(1000))')
    conn.commit()
    cursor.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Новая Интеграция', url='https://www.notion.so/my-integrations'))
    with open('photos/1.png', 'rb') as photo:
        msg1 = await message.answer_photo(photo, caption='Здравствуйте! Создайте новую интеграцию по ссылке:',
                                          reply_markup=markup)
    with open('photos/2.png', 'rb') as photo:
        msg2 = await message.answer_photo(photo, caption='Скопировуйте notion token.')
    msg3 = await message.answer("Введите notion token:")
    message_delete[message.chat.id] = [msg3.message_id, msg2.message_id, msg1.message_id]

    await Form.waiting_token.set()


@dp.message_handler(commands=['add'])
async def process_start_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название дедлайна:")
    await Form.add_title.set()


def calender_buttons_for_add(today, title):
    calendar = Calendar()
    weeks = calendar.monthdays2calendar(today.year, today.month)

    markup = types.InlineKeyboardMarkup(row_width=8)
    previous = types.InlineKeyboardButton(text="<-----------", callback_data=f'preq/{title}/{today}')
    next = types.InlineKeyboardButton(text="----------->", callback_data=f'nexq/{title}/{today}')

    markup.row(previous, next)

    monday_ = types.InlineKeyboardButton(text="Пн", callback_data='skip')
    tuesday_ = types.InlineKeyboardButton(text="Вт", callback_data='skip')
    wednesday_ = types.InlineKeyboardButton(text="Ср", callback_data='skip')
    thursday_ = types.InlineKeyboardButton(text="Чт", callback_data='skip')
    friday_ = types.InlineKeyboardButton(text="Пт", callback_data='skip')
    saturday_ = types.InlineKeyboardButton(text="Сб", callback_data='skip')
    sunday_ = types.InlineKeyboardButton(text="Вс", callback_data='skip')

    markup.row(monday_, tuesday_, wednesday_,
               thursday_, friday_, saturday_, sunday_)

    for week in weeks:
        markup_row_ = list()
        for day in week:
            number = day[0]
            button = types.InlineKeyboardButton(str(number),
                                                callback_data=f'addd/{title}/{str(today)[:8]}{str(number) if len(str(number))>=2 else f"0{str(number)}"}')
            markup_row_.append(button)
        markup.row(*markup_row_)
    return markup


@dp.message_handler(state=Form.add_title)
async def process_name(message: types.Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)
    today = date.today()
    markup = calender_buttons_for_add(today, title)
    await message.answer(f"Выберите дату дедлайна:")
    await message.answer(f"Текущая дата: {months[today.month - 1]} {today.year} Года", reply_markup=markup)
    await state.finish()


@dp.message_handler(state=Form.waiting_token)
async def process_name(message: types.Message, state: FSMContext):
    user_token = message.text
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass

    conn = sqlite3.connect("data/tokens.sql")
    cursor = conn.cursor()
    cursor.execute(
        f'INSERT INTO tokens_tbl (userid, NotionToken) VALUES ("%s", "%s")' % (str(message['from']['id']), user_token))
    cursor.execute('UPDATE tokens_tbl SET NotionToken=? WHERE userid=?', (user_token, (str(message['from']['id']))))
    conn.commit()
    cursor.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('View Notion', url='https://www.notion.so/product'))
    with open('photos/3.png', 'rb') as photo:
        msg1 = await message.answer_photo(photo,
                                          caption='Зайдите в ваш календарь, нажмите на … и добавьте соединение с вашей интеграцией (add connection)',
                                          reply_markup=markup)
    with open('photos/4.png', 'rb') as photo:
        msg2 = await message.answer_photo(photo,
                                          caption="Нажмите Share и скопируйте ссылку. Это и будет database token")
    msg3 = await message.answer(f"Введите notion database token:")
    message_delete[message.chat.id] = [msg3.message_id, msg2.message_id, msg1.message_id, message.message_id]
    await Form.waiting_database_token.set()


@dp.message_handler(state=Form.waiting_database_token)
async def process_token(message: types.Message, state: FSMContext):
    message_delete.get(message.chat.id, []).append(message.message_id)
    for message_id in message_delete.get(message.chat.id, []):
        try:
            await bot.delete_message(message.chat.id, message_id)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass
    message_delete.pop(message.chat.id)
    user_token = message.text
    user_token = user_token.split('?')[0].split('/')[-1]
    conn = sqlite3.connect("data/tokens.sql")
    cursor = conn.cursor()

    userid = str(message['from']['id'])
    new_token = user_token

    cursor.execute(
        f'INSERT INTO tokens_tbl (userid, DBToken) VALUES ("%s", "%s")' % (userid, new_token))
    cursor.execute('UPDATE tokens_tbl SET DBToken=? WHERE userid=?', (new_token, userid))
    conn.commit()

    cursor.close()
    conn.close()

    await message.answer(f"Нажмите /deadline для подключения календаря")
    await state.finish()


def calender_buttons(today):
    calendar = Calendar()
    weeks = calendar.monthdays2calendar(today.year, today.month)

    markup = types.InlineKeyboardMarkup(row_width=8)
    previous = types.InlineKeyboardButton(text="<-----------", callback_data=f'prev{today}')
    next = types.InlineKeyboardButton(text="----------->", callback_data=f'next{today}')

    markup.row(previous, next)

    monday_ = types.InlineKeyboardButton(text="Пн", callback_data='skip')
    tuesday_ = types.InlineKeyboardButton(text="Вт", callback_data='skip')
    wednesday_ = types.InlineKeyboardButton(text="Ср", callback_data='skip')
    thursday_ = types.InlineKeyboardButton(text="Чт", callback_data='skip')
    friday_ = types.InlineKeyboardButton(text="Пт", callback_data='skip')
    saturday_ = types.InlineKeyboardButton(text="Сб", callback_data='skip')
    sunday_ = types.InlineKeyboardButton(text="Вс", callback_data='skip')

    markup.row(monday_, tuesday_, wednesday_,
               thursday_, friday_, saturday_, sunday_)

    for week in weeks:
        markup_row_ = list()
        for day in week:
            number = day[0]
            button = types.InlineKeyboardButton(str(number), callback_data=f'exdt{str(today)[:8]}{str(number) if len(str(number))>=2 else f"0{str(number)}"}')
            markup_row_.append(button)
        markup.row(*markup_row_)
    return markup


@dp.message_handler(commands=['deadline'])
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


def change_date_by_months(date_str, months_to_add):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    new_date = date + relativedelta(months=months_to_add)
    return new_date


@dp.callback_query_handler(lambda c: c.data not in ['skip'])
async def callback(call):
    UserID = call['from']['id']
    if 'preq' in call.data:
        extraa, title, today = str(call.data).split('/')
        # today = str(call.data)[4:14]  # '2023-12-25'
        today = change_date_by_months(today.split()[0], -1)
        markup = calender_buttons_for_add(today, title)
        await call.message.delete()
        await call.message.answer(f"Текущая дата: {months[today.month - 1]} {today.year} Года", reply_markup=markup)

    if 'nexq' in call.data:
        extraa, title, today = str(call.data).split('/')
        # today = str(call.data)[4:14]  # '2023-12-25'
        today = change_date_by_months(today.split()[0], 1)
        markup = calender_buttons_for_add(today, title)
        await call.message.delete()
        await call.message.answer(f"Текущая дата: {months[today.month - 1]} {today.year} Года", reply_markup=markup)
    if 'prev' in call.data:
        today = str(call.data)[4:14]  # '2023-12-25'
        today = change_date_by_months(today, -1)
        markup = calender_buttons(today)
        await call.message.delete()
        await call.message.answer(f"Текущая дата: {months[today.month - 1]} {today.year} Года", reply_markup=markup)

    if 'next' in call.data:
        today = str(call.data)[4:14]  # '2023-12-25'
        today = change_date_by_months(today, 1)
        markup = calender_buttons(today)
        await call.message.delete()
        await call.message.answer(f"Текущая дата: {months[today.month - 1]} {today.year} Года", reply_markup=markup)
    if 'exdt' in call.data:
        print(call.data)
        today = str(call.data)[4:]
        all_dd_per_day = test_function(get_data_from_json_for_calendar(UserID, today))
        for dd in all_dd_per_day:
            await call.message.answer(dd)
        if not all_dd_per_day:
            await call.message.answer(f'No deadlines at {today}')
    if 'addd' in call.data:
        eventsdata = call.data
        extraa, title, date_of_event = eventsdata.split('/')
        userID = dict(call).get('from').get('id')
        create_page(title, userID, date_of_event)
        await call.message.delete()
        await call.message.answer(f"Notion Calendar обновлён")
    if len(str(call.data)) == 2:
        answer = connectin_check_time(dict(call).get('from').get('id'))
        if answer != Mistake:
            all_dd = test_function(answer_deadline_filter(call.data, answer))
            num, timedwm = call.data
            num = int(num)
            days_utill_dd = num if timedwm == 'd' else num * 7 if timedwm == 'w' else num * 30
            if num == 1:
                await call.message.answer(f'Deadlines for today:')
            else:
                await call.message.answer(f'Deadlines for {days_utill_dd} days:')
            for dd in all_dd:
                await call.message.answer(dd)
        else:
            await call.message.answer(f'{Mistake} Нажмите /start')


@dp.message_handler(commands=['calendar'])
async def show_calendar(message):
    today = date.today()
    markup = calender_buttons(today)
    await message.answer(f"Текущая дата: {months[today.month - 1]} {today.year} Года", reply_markup=markup)


executor.start_polling(dp)
