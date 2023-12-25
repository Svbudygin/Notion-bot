from aiogram import Bot, Dispatcher, executor, types
from config import TG_token, filename2
from main import test_function, answer_deadline_filter

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
    all_dd=test_function(answer_deadline_filter(call.data, filename2))
    for dd in all_dd:
        await call.message.answer(dd)


executor.start_polling(dp)
