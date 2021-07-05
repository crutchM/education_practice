import telebot
from telebot import types
import data_base
from user import User
import datetime
now = datetime.datetime.now()
bot = telebot.TeleBot('1706939990:AAEQ2KZ4VRbincT7Sa9TvaL-FRJ7SiD6Z08')
sort = {'По умолчанию': 101, 'Дешевле': 1, 'Дороже': 2, 'По дате (новые)': 104}


def newButton(text):
    return types.KeyboardButton(text)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать')
    bot.send_message(message.chat.id, 'Укажите свое местоположение в формате: "город улица дом"')
    msg = bot.send_message(message.chat.id, "Пример: Челябинск Молодогвардейцев 16")
    data_base.addUser(User("user", message.chat.id, now.strftime("%y-%m-%d"), None, None, message.text))
    bot.register_next_step_handler(msg, savePlace)


def mainMenu(message):
    user = bot.get_chat(message.chat.id).username
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = newButton('Сделать запрос')
    itembtn2 = newButton('Указать адрес')
    itembtn3 = newButton('Избранное')
    itembtn4 = newButton('История')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    if message.text.lower() == 'сделать запрос':
        markup = types.ReplyKeyboardMarkup(row_width=5)
        itembtn1 = newButton('Радиус')
        itembtn2 = newButton('Цены')
        itembtn3 = newButton('Рейтинг продавца')
        itembtn4 = newButton('Сортировка')
        itembtn5 = newButton('Модель видеокарты')
        itembtn6 = newButton('Главное меню')
        itembtn7 = newButton('Выполнить поиск')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
        markup.add(itembtn7)
        markup.add(itembtn6)
        msg = bot.send_message(message.chat.id, "Вы перешли в меню поиска", reply_markup=markup)
        bot.register_next_step_handler(msg, filterMenu)

    elif message.text.lower() == 'указать адрес':
        msg = bot.send_message(message.chat.id, "Вы в меню выбора локации")
        bot.send_message(message.chat.id, 'Укажите свое местоположение в формате: "город улица дом"')
        bot.send_message(message.chat.id, 'Пример: Челябинск Молодогвардейцев 16')
        bot.register_next_step_handler(msg, savePlace)
    else:
        bot.send_message(message.chat.id, "Здравствуйте, " + user + "ваш ID: " + str(message.chat.id) + ", Вы находитесь в главном меню. Выберите действие",
                         reply_markup=markup)


def filterMenu(message):
    markup = types.ReplyKeyboardMarkup(row_width=5)
    itembtn1 = newButton('Радиус')
    itembtn2 = newButton('Цены')
    itembtn3 = newButton('Рейтинг продавца')
    itembtn4 = newButton('Сортировка')
    itembtn5 = newButton('Модель видеокарты')
    itembtn6 = newButton('Главное меню')
    itembtn7 = newButton('Выполнить поиск')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    markup.add(itembtn7)
    markup.add(itembtn6)

    if message.text.lower() == 'радиус':
        chooseRadius(message)
    elif message.text.lower() == 'цены':
        choosePrice(message)
    elif message.text.lower() == 'рейтинг продавца':
        chooseRate(message)
    elif message.text.lower() == 'сортировка':
        chooseSort(message)
    elif message.text.lower() == 'модель видеокарты':
        chooseVideocard(message)
    elif message.text.lower() == 'главное меню':
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    elif message.text.lower() == 'выполнить поиск':
        # срабатывает поиск
        pass
    else:
        bot.send_message(message.chat.id, 'Выбери свою судьбу:', reply_markup=markup)


def chooseRadius(message):
    markup = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
    btn1 = newButton('1')
    btn2 = newButton('5')
    btn3 = newButton('10')
    btn4 = newButton('25')
    btn5 = newButton('50')
    btn6 = newButton('100')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    msg = bot.send_message(message.chat.id, "Выберите радиус", reply_markup=markup)
    bot.register_next_step_handler(msg, saveRadius)


def saveRadius(message):
    ##сохранить радиус
    msg = bot.send_message(message.chat.id, 'Сохранен радиус : ' + message.text + ' !')
    bot.register_next_step_handler(msg, filterMenu)
    filterMenu(message)


def savePlace(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    # сохранить местоположение
    if len(message.text.split(' ')) == 3:
        msg = bot.send_message(message.chat.id, "Сохранено местоположение: " + message.text + " !")
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)

    else:
        msg = bot.send_message(message.chat.id, 'Некорректные данные, попробуйте еще раз')
        bot.register_next_step_handler(msg, savePlace)


def choosePrice(message):
    markup = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
    btn1 = newButton('Указать минимум')
    btn2 = newButton('Указать максимум')
    markup.add(btn1, btn2)
    msg = bot.send_message(message.chat.id, "Укажите ограничение цен", reply_markup=markup)
    bot.register_next_step_handler(msg, savePrice)


def savePrice(message):
    if message.text == 'Указать минимум':
        msg = bot.send_message(message.chat.id, "Введите минимальную цену", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, ifMinPrice)
    elif message.text == 'Указать максимум':
        msg = bot.send_message(message.chat.id, "Введите максимальную цену", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, ifMaxPrice)
    else:
        bot.send_message(message.chat.id, 'ошибка')


def ifMinPrice(message):
    msg = bot.send_message(message.chat.id, 'Сохранена минмальная цена : ' + message.text + ' !')
    bot.register_next_step_handler(msg, filterMenu)
    filterMenu(message)
    # save in DB


def ifMaxPrice(message):
    msg = bot.send_message(message.chat.id, 'Сохранена максимальная цена : ' + message.text + ' !')
    bot.register_next_step_handler(msg, filterMenu)
    filterMenu(message)
    # save in DB


def chooseRate(message):
    msg = bot.send_message(message.chat.id, "Введите рейтинг (поддерживаются числа с плавающей точкой 0-5)",
                           reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, saveRate)


def saveRate(message):
    if float(message.text) < 0 or float(message.text) > 5:
        msg = bot.send_message(message.chat.id, 'Некорректные данные ' + message.text + ' !')
        bot.register_next_step_handler(msg, filterMenu)
        filterMenu(message)
    else:
        # сохранить рейтинг
        msg = bot.send_message(message.chat.id, 'Сохранен рейтинг : ' + message.text + ' !')
        bot.register_next_step_handler(msg, filterMenu)
        filterMenu(message)


def chooseSort(message):
    markup = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
    btn1 = newButton('По умолчанию')
    btn2 = newButton('Дешевле')
    btn3 = newButton('Дороже')
    btn4 = newButton('По дате (новые)')
    markup.add(btn1, btn2, btn3, btn4)
    msg = bot.send_message(message.chat.id, "Введите способ сортировки", reply_markup=markup)
    bot.register_next_step_handler(msg, saveSort)


def saveSort(message):
    # сохранить сортировку в зависимости от выбора
    msg = bot.send_message(message.chat.id, 'Сохранена сортировка : ' + message.text + ' !')
    bot.register_next_step_handler(msg, filterMenu)
    filterMenu(message)


def chooseVideocard(message):
    msg = bot.send_message(message.chat.id, "Введите модель видеокарты", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, saveVideocard)


def saveVideocard(message):
    # сохранить видеокарту
    msg = bot.send_message(message.chat.id, 'Сохранена видеокарта : ' + message.text + ' !')
    bot.register_next_step_handler(msg, filterMenu)
    filterMenu(message)


bot.polling(none_stop=True)
