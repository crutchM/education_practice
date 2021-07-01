from telebot import TeleBot

bot = TeleBot('1706939990:AAEQ2KZ4VRbincT7Sa9TvaL-FRJ7SiD6Z08')

@bot.message_handler(content_types=['text'])
def hi(message):
    bot.send_message(message.from_user.id,  "ку")

bot.polling()