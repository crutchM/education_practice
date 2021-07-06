import telebot
from telebot import types
import data_base
from user import User
import datetime
from Query import Query
from Ad import Advertisement

now = datetime.datetime.now()
bot = telebot.TeleBot('1860264884:AAGUDK2euWD_2UswRfGzyc_i-Hqz0MTJu7o')
sort = {'По умолчанию': 101, 'Дешевле': 1, 'Дороже': 2, 'По дате (новые)': 104}
testInc = 0


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

def newButton(text):
    return types.KeyboardButton(text)


@bot.message_handler(commands=['start'])
def start(message):
    if data_base.isUsrExists(message.chat.id):
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать')
        bot.send_message(message.chat.id, 'Укажите свое местоположение в формате: "город улица дом"')
        msg = bot.send_message(message.chat.id, "Пример: Челябинск Молодогвардейцев 16")
        bot.register_next_step_handler(msg, savePlace)


def savePlace(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if len(message.text.split(' ')) == 3:
        msg = bot.send_message(message.chat.id, "Сохранено местоположение: " + message.text + " !")
        user = User("user", message.chat.id, now.strftime("%y-%m-%d"), None, None, message.text, None)
        data_base.addUser(user)
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        msg = bot.send_message(message.chat.id, 'Некорректные данные, попробуйте еще раз')
        bot.register_next_step_handler(msg, savePlace)


def mainMenu(message):
    queries = {}
    queries[message.chat.id] = Query(sort=101, chipName='2070', sellerRate="0")

    def filterMenu(message):
        def chooseVideocard(message):
            msg = bot.send_message(message.chat.id, "Введите модель видеокарты",
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, saveVideocard)


        def saveVideocard(message):
            msg = bot.send_message(message.chat.id, 'Сохранена видеокарта : ' + message.text + ' !')
            queries[message.chat.id].chipName = message.text
            bot.register_next_step_handler(msg, filterMenu)
            filterMenu(message)

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
            queries[message.chat.id].rad = message.text
            msg = bot.send_message(message.chat.id, 'Сохранен радиус : ' + message.text + ' !')
            bot.register_next_step_handler(msg, filterMenu)
            filterMenu(message)



        def choosePrice(message):
            markup = types.ReplyKeyboardMarkup(row_width=6, resize_keyboard=True)
            btn1 = newButton('Указать минимум')
            btn2 = newButton('Указать максимум')
            markup.add(btn1, btn2)
            msg = bot.send_message(message.chat.id, "Укажите ограничение цен", reply_markup=markup)
            bot.register_next_step_handler(msg, savePrice)

        def savePrice(message):
            if message.text == 'Указать минимум':
                msg = bot.send_message(message.chat.id, "Введите минимальную цену",
                                       reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, ifMinPrice)
            elif message.text == 'Указать максимум':
                msg = bot.send_message(message.chat.id, "Введите максимальную цену",
                                       reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, ifMaxPrice)
            else:
                bot.send_message(message.chat.id, 'ошибка')

        def ifMinPrice(message):
            msg = bot.send_message(message.chat.id, 'Сохранена минмальная цена : ' + message.text + ' !')
            bot.register_next_step_handler(msg, filterMenu)
            filterMenu(message)
            queries[message.chat.id].minCost = int(message.text)


        def ifMaxPrice(message):
            msg = bot.send_message(message.chat.id, 'Сохранена максимальная цена : ' + message.text + ' !')
            bot.register_next_step_handler(msg, filterMenu)
            filterMenu(message)
            queries[message.chat.id].maxCost = int(message.text)

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
            queries[message.chat.id].sort = sort[message.text]
            msg = bot.send_message(message.chat.id, 'Сохранена сортировка : ' + message.text + ' !')
            bot.register_next_step_handler(msg, filterMenu)
            filterMenu(message)


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
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = newButton('⬅')
            itembtn2 = newButton('➡')
            itembtn3 = newButton('Добавить в избранное')
            itembtn4 = newButton('Главное меню')
            markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

            q = Query(queries[message.chat.id].chipName)
            advList = [*q.getAds('Челябинск').__next__()]

            # advList = [Advertisement(1000, 'Дешманская карточка 3070', 'Ссылочкамана'),
            #            Advertisement(5000, 'Intel HD Graphics', 'Ссылочкамана'),
            #            Advertisement(6000, 'Женщина в рабство', 'Ссылочкамана'),
            #            Advertisement(150000, 'Выгодно! Nvidia GeForce 9800', 'Ссылочкамана')]
            msg = bot.send_message(message.chat.id, "Вы перешли в меню поиска", reply_markup=markup)
            bot.register_next_step_handler(msg, doSearch)
            doSearch(message, advList, 0)
        else:
            scatter = "Разброс: " + (str(queries[message.chat.id].minCost) if not "None" else "0") + " - " + (str(queries[message.chat.id].minCost) if not "None" else "Не указано")
            sortType = "Сортировка: " + str(get_key(sort, queries[message.chat.id].sort))
            rate = "Минимальный рейтинг продавца в звездах: " + queries[message.chat.id].sellerRate
            bot.send_message(message.chat.id, 'Ваши текущие настройки:' + "\n" + "Радиус: " + str(queries[message.chat.id].rad) + "\n" +
            scatter + "\n" + sortType + "\n" + "Видеокарта: " + queries[message.chat.id].chipName + "\n" +
            rate, reply_markup=markup)

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
        bot.send_message(message.chat.id, "Здравствуйте, " + user + " ваш ID: " + str(
            message.chat.id) + ", Вы находитесь в главном меню. Выберите действие",
                         reply_markup=markup)


def doSearch(message, advList, index):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = newButton('⬅')
    itembtn2 = newButton('➡')
    itembtn3 = newButton('Добавить в избранное')
    itembtn4 = newButton('Главное меню')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    if message.text == 'Главное меню':
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    elif message.text == '⬅':
        if index - 3 < 0:
            msg = bot.send_message(message.chat.id, 'Вы в начале списка')
            bot.register_next_step_handler(msg, doSearch, advList, index)
        else:
            counter = 0
            for i in range(index-3, len(advList)):
                if counter < 3:
                    bot.send_message(message.chat.id, "Номер текущего объявления: " + str(i) + '\n' + advList[i].show())
                    counter += 1
                else:
                    break
            msg = bot.send_message(message.chat.id, 'Выберите действие')
            bot.register_next_step_handler(msg, doSearch, advList, index-3)
    elif message.text == '➡':
        if index+3 >= len(advList):
            msg = bot.send_message(message.chat.id, 'Вы в конце списка')
            bot.register_next_step_handler(msg, doSearch, advList, index)
        else:
            counter = 0
            for i in range(index+3, len(advList)):
                if counter < 3:
                    bot.send_message(message.chat.id, "Номер текущего объявления: " + str(i) + '\n' + advList[i].show())
                    counter += 1
                else:
                    break
            msg = bot.send_message(message.chat.id, 'Выберите действие')
            bot.register_next_step_handler(msg, doSearch, advList, index+3)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Результаты поиска:")
        counter = 0
        for i in range(index, len(advList)):
            if counter < 3:
                bot.send_message(message.chat.id, "Номер текущего объявления: " + str(i) + '\n' + advList[i].show())
                counter += 1
            else:
                break
        msg = bot.send_message(message.chat.id, 'Выберите действие')
        bot.register_next_step_handler(msg, doSearch, advList, index)


bot.polling(none_stop=True)
