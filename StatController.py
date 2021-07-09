from avitoParser import AvitoParser
from Query import Query
from db_helper import db_helper
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

dbh = db_helper()


def buildPriceSpreadChart(chip: str):  # график разброса цены
    values = dbh.getSpreadVal(chip)  # 0 рос 1 чел
    stat = [values[1], values[0]]
    label = ['Челябинская область', 'Россия']
    for i in range(2):
        if len(stat[i]) == 0:
            stat[i] = stat[i] + '0'
        v = [int(j) for j in stat[i].split()]
        v.sort()
        vmean = np.mean(v)
        vstd = np.std(v)
        pdf = stats.norm.pdf(v, vmean, vstd)
        plt.plot(v, pdf, label=label[i])

    plt.xlabel("Стоимость")
    plt.title("Разброс цен на видеокарты")
    png = plt.savefig('huita.png')
    plt.clf()
    return png


def buildHistChart(date: list, values: list, ylabel: str, title: str):  # график изменения цены со временем

    plt.plot(date, values)

    plt.xlabel("День")
    plt.ylabel(ylabel)
    plt.title(title)
    png = plt.savefig('huita.png')
    plt.clf()
    return png


def buildNewUsersChart():  # график регистраций в день пользователь
    data = dbh.getUsrsByDate()
    date, count = [], []
    for d in data:
        date.append(d[0])
        count.append(d[1])
    return buildHistChart(date=date, values=count, ylabel='кол-во новеньких', title='Регистраций в день')


def buildVisitsChart():  # график посещений
    data = dbh.getVisits()
    date, count = [], []
    for d in data:
        date.append(d[0])
        count.append(d[1])
    return buildHistChart(date=date, values=count, ylabel='кол-во посещений', title='Запросов в день')


def buildFavouritesPriceChart(id, link):
    data = dbh.getDateAndPrices(id, link)
    date, price = data[0], data[1]
    return buildHistChart(date=date, values=price, ylabel='стоимость', title='Изменение цены товара')


def buildAvgPriceChart(chip: str):
    data = dbh.getPriceAndDateList()  # 0 rus 1 chel 2 date
    date, val = data[2], [data[0], data[1]]
    label = ['Россия', 'Челябинская область']
    for i in range(2):
        plt.plot(date, val[i], label=label[i])

    plt.xlabel("День")
    plt.ylabel('Средняя стоимость')
    plt.title('Изменение средней цены отслеживаемого')
    png = plt.savefig('huita.png')
    plt.clf()
    return png


def getMonitoringStat():  # херня сама записывает стату из списка мониторинга в две таблицы
    locations = ['челябинская_область', 'россия']
    chips = dbh.getChips()

    for chip in chips:
        averages = []  # первое среднее челябы для чипа, второе для россии
        spread_values = []  # первое разброс челябы для чипа, второе для россии

        for loc in locations:
            temp_chip = prepareChipToMonitor(chip)
            q = Query(chipName=temp_chip)
            ads = attachLists(q.getAds(loc))
            avg = 0
            values = ''

            for ad in ads:
                cost = ad.cost
                if cost is not None:
                    avg += ad.cost
                    values += str(cost) + ' '
            averages.append(avg)
            spread_values.append(values)
        dbh.setValToSpread(chip, values_chel=spread_values[0], values_rus=spread_values[1])
        dbh.addToPriceStat(chip, avg_chel=averages[0], avg_rus=averages[1])


def getFavouritesStat():
    fav = dbh.getFavourites() #получаю список избранного из бд 0-id,  1-usr , 2-link TEXT,  3-price, 4-name TEXT,
    ap = AvitoParser()
    favs = [(f[0],f[2]) for f in fav]
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        fav = list(executor.map(ap.parsePrice, favs))
    for f in fav:
        id = f[0]
        price = f[1]
        dbh.AddToFavChanges(id, price)
    dbh.updatePrices()


def attachLists(generator):
    values = []
    for i in generator:
        values.extend(i)
    return values


def prepareChipToMonitor(chip: str):
    tok = chip.split('+')
    tok[0] = f'%27{tok[0]}%27'
    return ' '.join(tok)

