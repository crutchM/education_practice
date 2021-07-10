import telebot
from telebot import types
import data_base
from db_helper import db_helper
from user import User
import datetime
from Query import Query
from Ad import Advertisement
import StatController as sc
import ChipsToMonitor as chips

bot = telebot.TeleBot('1860264884:AAGUDK2euWD_2UswRfGzyc_i-Hqz0MTJu7o')
sort = {'По умолчанию': 101, 'Дешевле': 1, 'Дороже': 2, 'По дате (новые)': 104}
testInc = 0
dba = db_helper()


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


def newButton(text):
    return types.KeyboardButton(text)


def getCorrectDate():
    return datetime.datetime.today().strftime("%Y-%m-%d-%H:%M:%S")


@bot.message_handler(commands=['start'])
def start(message):
    if dba.isUsrExists(message.chat.id):
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать')
        bot.send_message(message.chat.id, 'Укажите город')
        msg = bot.send_message(message.chat.id, "Пример: Челябинск")
        bot.register_next_step_handler(msg, choosePlace, message)


def choosePlace(message, msge=None):
    def saveCity(city):
        return city.lower().replace(' ', '-')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    city = saveCity(message.text)

    msg = bot.send_message(message.chat.id, "Введите улицу и дом, например: Молодогвардейцев 74")
    bot.register_next_step_handler(msg, chooseStreet, city, msge)


def statMenu(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if message.text.lower() == 'новые пользователи':
        newUsersStat(message)
    elif message.text.lower() == 'запросы по дням':
        visitsStat(message)
    elif message.text.lower() == 'история запросов':
        queriesStat(message)
    else:
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)

def newUsersStat(message):
    sc.buildNewUsersChart()
    bot.send_photo(message.chat.id, photo=open('huita.png', 'rb'))
    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Вы в главном меню')
    bot.register_next_step_handler(msg, mainMenu)
    message.text = '/start'
    mainMenu(message)


def visitsStat(message):
    sc.buildVisitsChart()
    bot.send_photo(message.chat.id, photo=open('huita.png', 'rb'))
    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Вы в главном меню')
    bot.register_next_step_handler(msg, mainMenu)
    message.text = '/start'
    mainMenu(message)

def queriesStat(message):
    usersId = dba.getUsersId()
    users = {}
    usersString = "Users: "
    for id in usersId:
        username = bot.get_chat(id).username
        users[id] = username
        usersString += "@" + username + ", "
    bot.send_message(message.chat.id, usersString)
    msg = bot.send_message(message.chat.id, 'Напишите ник пользователя без \'@\' ')
    bot.register_next_step_handler(msg, sendQueriesStatByUser, users)


def sendQueriesStatByUser(message, dict):
    if message.text in dict.values() and dba.isUsrExists(get_key(dict, message.text)):
        queriesHistory = ""
        for query in dba.getQuriesHistory(get_key(dict, message.text)):
            radius = "Радиус: "
            rate = "Минимальный рейтинг продавца в звездах: "
            if query.rad is None:
                radius += "Не указан, "
            else:
                radius += str(query.rad) + "км, "
            if query.sellerRate is None:
                rate += "Не указан"
            else:
                rate += str(query.sellerRate)
            minPrice = "0"
            maxPrice = "Не указано"
            if query.minCost is not None:
                minPrice = str(query.minCost)
            if query.maxCost is not None:
                maxPrice = str(query.maxCost)
            scatter = "Разброс: " + minPrice + " - " + maxPrice
            sortType = "Сортировка: " + str(get_key(sort, query.sort))
            queriesHistory += "Видеокарта: " + query.chipName + ", " + radius + scatter + ", " + "\n" + sortType + ", " + rate + "\n\n"
        if not queriesHistory:
            msg = bot.send_message(message.chat.id, 'История юзера пуста')
            bot.register_next_step_handler(msg, mainMenu)
        else:
            msg = bot.send_message(message.chat.id, queriesHistory)
            bot.register_next_step_handler(msg, mainMenu)
    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Вы в главном меню')
    bot.register_next_step_handler(msg, mainMenu)
    message.text = '/start'
    mainMenu(message)

def selectUser(message, usersDict):
    bot.clear_step_handler_by_chat_id(message.chat.id)  # не факт что нужно
    msg = bot.send_message(message.chat.id, 'Напишите роль user или admin')
    bot.register_next_step_handler(msg, saveUserRole, get_key(usersDict, message.text), usersDict)


def saveUserRole(message, id, usersDict):
    bot.clear_step_handler_by_chat_id(message.chat.id)  # не факт что нужно
    if message.text.lower() == 'user' or message.text.lower() == 'admin':
        dba.updateUsrRole(id, message.text.lower())
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        msg = bot.send_message(message.chat.id, 'Некорректные данные')
        bot.register_next_step_handler(msg, selectUser, usersDict)
        selectUser(message, usersDict)


def chooseStreet(message, city, msge):
    if msge.text == 'Указать адрес':
        msge.text = '/start'
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if dba.isUsrExists(message.chat.id):
        dba.updateLoc(message.chat.id, city + " " + message.text)
        bot.register_next_step_handler(msge, mainMenu)
        mainMenu(msge)
    else:
        registerUser(message, city + " " + message.text)
        bot.register_next_step_handler(msge, mainMenu)
        mainMenu(msge)


def registerUser(message, location):
    dba.addUser(message.chat.id, 'admin', location)
    for chip in chips.chips:
        dba.addCard(message.chat.id, chip)
        dba.setValToSpread(chip, "0", "0")


def chipMonitoring(message):
    myChips = [i.split('+') for i in dba.getChipsByID(message.chat.id)]
    myChipsInDB = dba.getChipsByID(message.chat.id)
    myChipsForAdding = []
    for chip in chips.chips:
        if chip not in myChipsInDB:
            myChipsForAdding.append(chip)
    if message.text == "Добавить чип":
        selectAddingChip(message, myChipsForAdding)
    elif message.text == "Удалить чип":
        selectRemovingChip(message, myChips)
    elif message.text == "Статистика по чипу" and len(myChips) != 0:
        selectChip(message, myChips)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)


def selectAddingChip(message,myChips):
    chipsString = ''
    for i in range(0, len(myChips)):
        chipsString += str(i) + ". " + myChips[i] + " "
        if i % 2 == 0:
            chipsString += '\n'
    if chipsString == "":
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "У вас полный набор чипов!")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        bot.send_message(message.chat.id, 'Список чипов, которые можно добавить: ' + '\n' + chipsString)
        msg = bot.send_message(message.chat.id, 'Введите номер чипа, который хотите добавить', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, addChip, myChips)


def addChip(message, myChips):
    if message.text.isdigit() and int(message.text) >= 0 and int(message.text) < len(myChips):
        chip = myChips[int(message.text)]
        dba.addCard(message.chat.id, chip)
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Добавлено!")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы ввели число не из диапазона")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)


def selectRemovingChip(message, myChips):
    msg = bot.send_message(message.chat.id, 'Введите номер чипа, который хотите удалить')
    bot.register_next_step_handler(msg, removeChip, myChips)



def removeChip(message, myChips):
    if message.text.isdigit() and int(message.text) >= 0 and int(message.text) < len(myChips):
        chip = dba.getChipsByID(message.chat.id)[int(message.text)]
        dba.deleteCard(message.chat.id, chip)
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Удалено!")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы ввели число не из диапазона")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)


def selectChip(message, myChips):
    msg = bot.send_message(message.chat.id, 'Введите номер чипа, статистика которого вас интересует')
    bot.register_next_step_handler(msg, getChipStat, myChips)


def getChipStat(message, myChips):
    if message.text.isdigit() and int(message.text) > 0 and int(message.text) < len(myChips):
        chip = dba.getChipsByID(message.chat.id)[int(message.text)]
        sc.buildAvgPriceChart(chip)
        bot.send_photo(message.chat.id, photo=open('huita.png', 'rb'))
        sc.buildPriceSpreadChart(chip)
        bot.send_photo(message.chat.id, photo=open('huita.png', 'rb'))
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы перешли в главное меню")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы ввели число не из диапазона")
        message.text = '/start'
        bot.register_next_step_handler(msg, mainMenu)
        mainMenu(message)



def mainMenu(message):
    queries = {}
    lastQuery = dba.getLastQuery(message.chat.id)
    if lastQuery is None:
        queries[message.chat.id] = Query(sort=101, chipName='2070', sellerRate=None)
    else:
        queries[message.chat.id] = lastQuery

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
            btn7 = newButton('Не указывать')
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
            markup.add(btn7)
            msg = bot.send_message(message.chat.id, "Выберите радиус", reply_markup=markup)

            bot.register_next_step_handler(msg, saveRadius)

        def saveRadius(message):
            if message.text in ['1', '5', '10', '25', '50', '100']:
                queries[message.chat.id].rad = message.text
                msg = bot.send_message(message.chat.id, 'Сохранен радиус : ' + message.text + ' !')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)
            elif message.text.lower() == 'не указывать':
                queries[message.chat.id].rad = None
                msg = bot.send_message(message.chat.id, 'Настройка радиуса сброшена')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)
            else:
                msg = bot.send_message(message.chat.id, 'Некорректные данные')
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
                msg = bot.send_message(message.chat.id, 'Некорректные жанные')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)

        def ifMinPrice(message):
            if message.text.isdigit():
                queries[message.chat.id].minCost = int(message.text)
                msg = bot.send_message(message.chat.id, 'Сохранена минимальная цена : ' + message.text + ' !')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)
            else:
                msg = bot.send_message(message.chat.id, 'Некорректные данные')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)

        def ifMaxPrice(message):
            if message.text.isdigit():
                mincost = 0
                if queries[message.chat.id].minCost is not None:
                    mincost = queries[message.chat.id].minCost

                if int(message.text) < mincost:
                    msg = bot.send_message(message.chat.id,
                                           'Максимальная цена должна быть больше или равна минимальной!')
                    bot.register_next_step_handler(msg, filterMenu)
                    filterMenu(message)
                else:
                    queries[message.chat.id].maxCost = int(message.text)
                    msg = bot.send_message(message.chat.id, 'Сохранена максимальная цена : ' + message.text + ' !')
                    bot.register_next_step_handler(msg, filterMenu)
                    filterMenu(message)
            else:
                msg = bot.send_message(message.chat.id, 'Некорректные данные')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)

        def chooseRate(message):
            msg = bot.send_message(message.chat.id, "Введите рейтинг (поддерживаются числа с плавающей точкой 0-5)",
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, saveRate)

        def saveRate(message):
            try:
                float(message.text)
                if float(message.text) < 0 or float(message.text) > 5:
                    msg = bot.send_message(message.chat.id, 'Некорректные данные ' + message.text + ' !')
                    bot.register_next_step_handler(msg, filterMenu)
                    filterMenu(message)
                else:
                    if float(message.text) == 0:
                        queries[message.chat.id].sellerRate = None
                    else:
                        queries[message.chat.id].sellerRate = float(message.text)
                    msg = bot.send_message(message.chat.id, 'Сохранен рейтинг : ' + message.text + ' !')
                    bot.register_next_step_handler(msg, filterMenu)
                    filterMenu(message)
            except ValueError:
                msg = bot.send_message(message.chat.id, 'Некорректные данные')
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
            if message.text in sort:
                queries[message.chat.id].sort = sort[message.text]
                msg = bot.send_message(message.chat.id, 'Сохранена сортировка : ' + message.text + ' !')
                bot.register_next_step_handler(msg, filterMenu)
                filterMenu(message)
            else:
                msg = bot.send_message(message.chat.id, 'Некорректные данные')
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
            itembtn4 = newButton('Главное меню')
            markup.add(itembtn1, itembtn2, itembtn4)
            dba.addToQueriesHistory(queries[message.chat.id], message.chat.id, getCorrectDate())
            # q = Query(queries[message.chat.id].chipName)
            # advList = [*q.getAds('Челябинск').__next__()]
            advList = [*queries[message.chat.id].getAds(usr.location.split(' ')[0]).__next__()]
            if len(advList) != 0:
                msg = bot.send_message(message.chat.id, "Вы перешли в меню поиска", reply_markup=markup)
                bot.register_next_step_handler(msg, doSearch)
                doSearch(message, advList, 0)
            else:
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
                msg = bot.send_message(message.chat.id, "Не найдено объявлений по таким фильтрам", reply_markup=markup)
                bot.register_next_step_handler(msg, filterMenu)


        else:
            radius = ""
            rate = "Минимальный рейтинг продавца в звездах: "
            if queries[message.chat.id].rad is None:
                radius = "Не указан"
            else:
                radius = str(queries[message.chat.id].rad)
            if queries[message.chat.id].sellerRate is None:
                rate += "Не указан"
            else:
                rate += str(queries[message.chat.id].sellerRate)
            minPrice = "0"
            maxPrice = "Не указано"
            if queries[message.chat.id].minCost is not None:
                minPrice = str(queries[message.chat.id].minCost)
            if queries[message.chat.id].maxCost is not None:
                maxPrice = str(queries[message.chat.id].maxCost)
            scatter = "Разброс: " + minPrice + " - " + maxPrice
            sortType = "Сортировка: " + str(get_key(sort, queries[message.chat.id].sort))
            bot.send_message(message.chat.id,
                             'Ваши текущие настройки:' + "\n" + "Радиус: " + radius + "\n" +
                             scatter + "\n" + sortType + "\n" + "Видеокарта: " + queries[
                                 message.chat.id].chipName + "\n" +
                             rate, reply_markup=markup)

    user = bot.get_chat(message.chat.id).username  # для приветствия
    usr = dba.getUser(message.chat.id)  # для обработки
    markup = types.ReplyKeyboardMarkup(row_width=4)
    itembtn1 = newButton('Сделать запрос')
    itembtn2 = newButton('Указать адрес')
    itembtn3 = newButton('Мониторинг чипов')
    itembtn4 = newButton('Избранное')
    itembtn5 = newButton('История')
    itembtn6 = newButton('Просмотр статистики')
    itembtn7 = newButton('Изменить роль')

    if usr.role == 'user':
        markup.add(itembtn1, itembtn2, itembtn3)
        markup.add(itembtn4, itembtn5)
    else:
        markup.add(itembtn1, itembtn2, itembtn3)
        markup.add(itembtn6, itembtn7, itembtn4, itembtn5)

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
        filterMenu(message)

    elif message.text.lower() == 'изменить роль' and dba.getUser(message.chat.id).role == 'admin':
        usersId = dba.getUsersId()
        users = {}
        usersString = "Users: "
        for id in usersId:
            username = bot.get_chat(id).username
            users[id] = username
            usersString +="@" + username + ", "
        bot.send_message(message.chat.id, usersString)
        msg = bot.send_message(message.chat.id, "Введите username пользователя")
        bot.register_next_step_handler(msg, selectUser, users)

    elif message.text.lower() == 'указать адрес':
        msg = bot.send_message(message.chat.id, "Вы в меню выбора локации")
        bot.send_message(message.chat.id, 'Укажите город')
        msg = bot.send_message(message.chat.id, "Пример: Челябинск")
        bot.register_next_step_handler(msg, choosePlace, message)

    elif message.text.lower() == 'просмотр статистики':
        markup = types.ReplyKeyboardMarkup(row_width=3)
        btn1 = newButton('Новые пользователи')
        btn2 = newButton('Запросы по дням')
        btn3 = newButton('История запросов')
        btn4 = newButton('Главное меню')
        markup.add(btn1, btn2, btn3, btn4)
        msg = bot.send_message(message.chat.id, "Выберите статистику", reply_markup=markup)
        bot.register_next_step_handler(msg, statMenu)


    elif message.text.lower() == 'мониторинг чипов':
        markup = types.ReplyKeyboardMarkup(row_width=3)
        itembtn1 = newButton('Добавить чип')
        itembtn2 = newButton('Удалить чип')
        itembtn3 = newButton('Статистика по чипу')
        itembtn4 = newButton('Главное меню')
        markup.add(itembtn1, itembtn2, itembtn3)
        markup.add(itembtn4)
        msg = bot.send_message(message.chat.id, "Вы в меню выбора чипов", reply_markup=markup)
        myChips = [i.split('+') for i in dba.getChipsByID(message.chat.id)]
        chipsString = ""
        for i in range(0, len(myChips)):
            chipsString += str(i) + ". " + myChips[i][0] + " "
            if i % 2 == 0:
                chipsString += '\n'
        if chipsString == "":
            bot.send_message(message.chat.id, 'Вы не следите ни за одним чипом')
        else:
            bot.send_message(message.chat.id, 'Список отслеживаемых чипов: ' + '\n' + chipsString)
        bot.register_next_step_handler(msg, chipMonitoring)

    elif message.text.lower() == 'избранное':
        advList = dba.getFavourites(message.chat.id)
        if len(advList) == 0:
            msg = bot.send_message(message.chat.id, 'Список избранного пуст')
            bot.register_next_step_handler(msg, mainMenu)
        else:
            msg = bot.send_message(message.chat.id, "Ваше избранное:")
            for adv in advList:
                removebtn = types.InlineKeyboardButton(text='Удалить', callback_data="remove")
                markup = types.InlineKeyboardMarkup()
                markup.add(removebtn)
                bot.send_message(msg.chat.id, adv.show(), reply_markup=markup)
            bot.register_next_step_handler(msg, mainMenu)
    elif message.text.lower() == 'история':
        queriesHistory = ""
        for query in dba.getQuriesHistory(message.chat.id):
            radius = "Радиус: "
            rate = "Минимальный рейтинг продавца в звездах: "
            if query.rad is None:
                radius += "Не указан, "
            else:
                radius += str(query.rad) + "км, "
            if query.sellerRate is None:
                rate += "Не указан"
            else:
                rate += str(query.sellerRate)
            minPrice = "0"
            maxPrice = "Не указано"
            if query.minCost is not None:
                minPrice = str(query.minCost)
            if query.maxCost is not None:
                maxPrice = str(query.maxCost)
            scatter = "Разброс: " + minPrice + " - " + maxPrice
            sortType = "Сортировка: " + str(get_key(sort, query.sort))
            queriesHistory += "Видеокарта: " + query.chipName + ", " + radius + scatter + ", " + "\n" + sortType + ", " + rate + "\n\n"
        if not queriesHistory:
            msg = bot.send_message(message.chat.id, 'Ваша история пуста')
            bot.register_next_step_handler(msg, mainMenu)
        else:
            msg = bot.send_message(message.chat.id, queriesHistory)
            bot.register_next_step_handler(msg, mainMenu)
    elif message.text == 'Вы перешли в главное меню' or message.text == '/start' or message.text == 'Главное меню' or message.text == 'Вы ввели некорректные данные':
        bot.send_message(message.chat.id, "Здравствуйте, " + user + " ваш ID: " + str(
            message.chat.id) + ", Ваш адрес: " + usr.location + ", Вы находитесь в главном меню. Выберите действие",
                         reply_markup=markup)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        msg = bot.send_message(message.chat.id, "Вы ввели некорректные данные", reply_markup=markup)
        bot.register_next_step_handler(msg, mainMenu)


def getUserAnswer(message, callback):
    msg = bot.send_message(message, 'Неверные данные, попробуйте еще раз')
    bot.register_next_step_handler(msg, callback)


def doSearch(message, advList, index):
    addbtn1 = types.InlineKeyboardButton(text='Добавить в избранное', callback_data=str(index))
    addbtn2 = types.InlineKeyboardButton(text='Добавить в избранное', callback_data=str(index + 1))
    addbtn3 = types.InlineKeyboardButton(text='Добавить в избранное', callback_data=str(index + 2))
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = newButton('⬅')
    itembtn2 = newButton('➡')
    itembtn4 = newButton('Главное меню')
    markup.add(itembtn1, itembtn2, itembtn4)
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
            for i in range(index - 3, len(advList)):
                if counter < 3:
                    inlineMarkup = types.InlineKeyboardMarkup()
                    inlineMarkup.add(types.InlineKeyboardButton(text='Добавить в избранное 💫',
                                                                callback_data=str(index - 3 + counter)))
                    bot.send_message(message.chat.id, "Номер текущего объявления: " + str(i) + '\n' + advList[i].show(),
                                     reply_markup=inlineMarkup)
                    counter += 1
                else:
                    break
            msg = bot.send_message(message.chat.id, 'Выберите действие')
            bot.register_next_step_handler(msg, doSearch, advList, index - 3)
    elif message.text == '➡':
        if index + 3 >= len(advList):
            msg = bot.send_message(message.chat.id, 'Вы в конце списка')
            bot.register_next_step_handler(msg, doSearch, advList, index)
        else:
            counter = 0
            for i in range(index + 3, len(advList)):
                if counter < 3:
                    inlineMarkup = types.InlineKeyboardMarkup()
                    inlineMarkup.add(types.InlineKeyboardButton(text='Добавить в избранное 💫',
                                                                callback_data=str(index + 3 + counter)))
                    bot.send_message(message.chat.id, "Номер текущего объявления: " + str(i) + '\n' + advList[i].show(),
                                     reply_markup=inlineMarkup)
                    counter += 1
                else:
                    break
            msg = bot.send_message(message.chat.id, 'Выберите действие')
            bot.register_next_step_handler(msg, doSearch, advList, index + 3)
    else:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Результаты поиска:")
        counter = 0
        for i in range(index, len(advList)):
            if counter < 3:
                inlineMarkup = types.InlineKeyboardMarkup()
                inlineMarkup.add(
                    types.InlineKeyboardButton(text='Добавить в избранное 💫', callback_data=str(index + counter)))
                bot.send_message(message.chat.id, "Номер текущего объявления: " + str(i) + '\n' + advList[i].show(),
                                 reply_markup=inlineMarkup)
                counter += 1
            else:
                break
        msg = bot.send_message(message.chat.id, 'Выберите действие')
        bot.register_next_step_handler(msg, doSearch, advList, index)


@bot.callback_query_handler(func=lambda call: True)
def addAdvinFvr(call):
    if call.data == 'remove':
        adv = call.message.text.split('\n')
        dba.delFromFav(call.message.chat.id, adv[4])
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, 'Удалено!')

    else:

        arr = call.message.text.split('\n')
        link = arr[5]
        cost = arr[3]
        name = arr[1]
        adv = Advertisement(link=link, cost=cost, name=name)
        favourites = dba.getFavourites(call.message.chat.id)
        linksOfFav = map(lambda x: x.link, favourites)
        if adv.link in linksOfFav:
            bot.send_message(call.message.chat.id, 'Уже есть в избранном')
        else:
            dba.addToFavourite(adv, call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Добавлено в избранное')


@bot.message_handler(content_types='text')
def incorrectInput(message):
    msg = bot.send_message(message.chat.id, "Зачем балуешься?")
    bot.register_next_step_handler(msg, mainMenu)
    mainMenu(message)


bot.polling(none_stop=True)
