import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import database

bot = telebot.TeleBot('6352909336:AAGIzccUfiU-p9LGLA6R1aKtz4pecz1tjRc')


def cats_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton("Спорт", callback_data="sport"), \
               InlineKeyboardButton("Программирование", callback_data="proga"), \
               InlineKeyboardButton("Мультики", callback_data="mult"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    database.insert_varible_into_table(call.from_user.id, call.data, 'text')
    if call.data == "sport":
        bot.send_message(call.from_user.id, "Отлично) подбираем тебе собеседников-спортсменов")
    if call.data == "proga":
        bot.send_message(call.from_user.id, "Отлично) подбираем тебе собеседников-программистов")
    if call.data == "mult":
        bot.send_message(call.from_user.id, "Отлично) подбираем тебе собеседников-еблуш, не придмал")
    bot.send_message(call.from_user.id, database.get_developer_info(call.from_user.id))


@bot.message_handler(commands=['start'])
def start(msg):
    text = f"Привет, {msg.from_user.first_name}! Я помогу тебе найти себе друга....(дописать текст " + \
            "Выбери категорию, в которой ты хочешь подбирать себе друга:"
    bot.send_message(msg.chat.id, text, reply_markup=cats_markup())


bot.infinity_polling()