import telebot


token = '2083034513:AAHg1npWs0ugdonQr4sPWj9KkUP8NDHPCRI'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    with open('file.txt', 'w') as f:
        f.write(str(message.chat.id))
    bot.send_message(message.chat.id, 'Привет')


bot.infinity_polling()
