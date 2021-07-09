import data_base
import datetime
import string
from Query import Query
from Ad import Advertisement
from user import User
class db_helper:

    def __init__(self):
        self.db = data_base.data_base()

    def addUser(self, id, role, location, regDate):
        self.db.curr.execute("INSERT INTO users VALUES(?,?,?,?);", (str(id), role, location, regDate))
        self.db.conn.commit()

    def isUsrExists(self, user):
        self.db.curr.execute("SELECT * FROM users WHERE id =" + str(user) + ";")
        return self.db.curr.fetchone() is not None

    def addToFavourite(self, advertisement, usrid):
        self.db.curr.execute("INSERT INTO favourites VALUES(NULL,?,?,?,?);",
                     (str(usrid), advertisement.link, advertisement.cost, advertisement.name))
        self.db.conn.commit()

    def addToQueriesHistory(self, query, id, date):
        self.db.curr.execute("INSERT INTO queries VALUES(?,?,?,?,?,?,?,?);",
                     (id, query.rad, query.minCost, query.maxCost, query.sellerRate, query.sort, query.chipName, date))
        self.db.conn.commit()

    def getFavourites(self, userid):
        self.db.curr.execute("SELECT * FROM FAVOURITES WHERE usr = " + str(userid) + ";")
        records = self.db.curr.fetchall()
        recordslist = []
        for row in records:
            recordslist.append(Advertisement(cost=row[3], name=row[4], link=row[2]))
        return recordslist

    def getQuriesHistory(self, userid):
        self.db.curr.execute("SELECT * FROM queries WHERE usr = ?;", (str(userid),))
        records = self.db.curr.fetchall()
        recordslist = []
        for row in records:
            recordslist.append(
                Query(chipName=row[6], sort=row[5], sellerRate=row[4], rad=row[1], minCost=row[2], maxCost=row[3]))
        return recordslist

    def getVisits(self):
        self.db.curr.execute("SELECT CONVERT(varchar(10),q.qdate,102), count(*) FROM queries q group by CONVERT(varchar(10),q.qdate,102);")
        records = self.db.curr.fetchall()
        stat = []  # format yyyy-mm-dd
        for row in records:
            stat.append((row[0], row[1]))
        return stat

    # def getVisits(self):
    #     self.db.curr.execute("SELECT strftime('%y-%m-%d', q.qdate), count(*) FROM queries q group by strftime('%y-%m-%d', q.qdate);")
    #     records = self.db.curr.fetchall()
    #     stat = []  # format yyyy-mm-dd
    #     for row in records:
    #         stat.append((row[0], row[1]))
    #     return stat

    def getLocation(self, id):
        self.db.curr.execute("SELECT location FROM users WHERE id = ?;", (str(id),))
        return self.db.curr.fetchone()

    def setValToSpread(self, chip, values_rus, values_chel):
        if self.db.curr.execute("SELECT * FROM price_spread_stat p WHERE p.chip = ?", (chip,)).fetchone() is None:
            self.db.curr.execute("INSERT INTO price_spread_stat VALUES (?,?,?)", (chip, values_rus, values_chel))
            self.db.conn.commit()
        else:
            self.db.curr.execute("UPDATE price_spread_stat set  values_rus = ?, values_chel = ? WHERE chip = ?",
                         (values_rus, values_chel, chip))
        self.db.conn.commit()

    def getPriceAndDateList(self, chip):
        self.db.curr.execute("SELECT * FROM avg_price_stat WHERE chip_name = ?", (chip,))
        rec = self.db.curr.fetchall()
        avg_chel = []
        avg_rus = []
        date = []
        for row in rec:
            avg_chel.append(row[1])
            avg_rus.append(row[3])
            date.append(row[2])
        return (avg_rus, avg_chel, date)

    def addCard(self, user, card):
        self.db.curr.execute("INSERT INTO cardList VALUES (?,?)", (card, user))
        self.db.conn.commit()

    def AddToFavChanges(self, id, price):
        date = datetime.datetime.now().strftime("%y-%m-%d")
        self.db.curr.execute("INSERT INTO favourites_price_change VALUES (?,?,?)", (id, price, date))
        self.db.conn.commit()

    def updatePrices(self):
        self.db.curr.execute("SELECT * FROM favourites")
        rec = self.db.curr.fetchall()
        list = []
        for row in rec:
            list.append(row[0])
        self.db.curr.execute("SELECT fdate FROM favourites_price_change ")
        recs = self.db.curr.fetchall()
        max_date = datetime.datetime.strptime("2020-07-07-22:15:10", "%Y-%m-%d-%H:%M:%S")
        for row in recs:
            cur_row = datetime.datetime.strptime(row[2], "%Y-%m-%d-%H:%M:%S")
            if max_date < cur_row:
                max_date = cur_row
        for id in list:
            self.updateOncePrice(id, self.getSum(id, max_date))
        self.db.conn.commit()

    def getSum(self, id, maxDate):
        recs = self.db.curr.execute("SELECT * FROM favourites_price_change").fetchall()
        for row in recs:
            if row[0] == id and maxDate == datetime.datetime.strptime(row[2], "%Y-%m-%d-%H:%M:%S"):
                return int(row[1])

    def updateOncePrice(self, id, sum):
        self.db.curr.execute("UPDATE favourites set price = ? where id = ?", (str(sum), str(id)))
        self.db.conn.commit()

    def doTest(self):
        self.db.curr.execute("INSERT INTO users VALUES(?,?,?,?);", (str(123), "usr.role", "usr.location", "2021-09-09"))
        self.db.curr.execute("INSERT INTO queries VALUES(?,?,?,?,?,?,?,?);",
                             (123, 3, 3, 5, 5, 1, "aboba",
                              "2021-09-09-21:57:22"))
        self.db.curr.execute("INSERT INTO queries VALUES(?,?,?,?,?,?,?,?);",
                             (123, 4, 4, 6, 6, 1, "eboba",
                              "2021-09-09-21:56:10"))

        self.db.conn.commit()
        return self.db.curr.execute("SELECT * FROM users").fetchone()
    def getUser(self, id):
        self.db.curr.execute("SELECT * FROM users WHERE id = ?", (str(id),))
        res = self.db.curr.fetchone()
        if res is None:
            return None
        return User(id=res[0], location=res[2], role=res[1], regDate=res[3])

    def getLastQuery(self, id):
        recs = self.db.curr.execute("SELECT * FROM  queries WHERE usr = ?", (str(id),)).fetchall()
        max_date = datetime.datetime.strptime("2020-07-07-22:15:10", "%Y-%m-%d-%H:%M:%S")
        for row in recs:
            cur_row = datetime.datetime.strptime(row[7], "%Y-%m-%d-%H:%M:%S")
            if max_date < cur_row:
                max_date = cur_row
        for row in recs:
            cur_row = datetime.datetime.strptime(row[7], "%Y-%m-%d-%H:%M:%S")
            if max_date == cur_row:
                return Query(chipName=row[6], sort=row[5], sellerRate=row[4], rad=row[1], minCost=row[2], maxCost=row[3])


    def updateLoc(self, id, location):
        self.db.curr.execute("UPDATE users set location = ? where id = ?", (location, id))
        self.db.conn.commit()

    def updateUsrRole(self, id, role):
        self.db.curr.execute("UPDATE users set role = ? where id = ?", (role, id))
        self.db.conn.commit()
    def delFromFav(self, user, link):
        self.db.currexecute("DELETE FROM favourites WHERE usr = ? AND link = ?", (user, link))
        self.db.conn.commit()

    def getFavouritesTuple(self):
        self.db.curr.execute("SELECT * from favourites")
        rec = self.db.curr.fetchall()
        res = []
        for row in rec:
            a = (row[0], row[1], row[2], row[3], row[4])
            res.append(a)
        return res

    def getChips(self):
        rec = self.db.curr.execute("SELECT chip FROM price_spread_stat").fetchall()
        res = []
        for row in rec:
            res.append(row[0])
        return res

    def addToPriceStat(self, chip, avg_chel, avg_rus):
        date = datetime.datetime.now().strftime("%y-%m-%d")
        self.db.curr.execute("INSERT INTO avg_price_stat VALUES (?, ?, ?, ?)", (chip, str(avg_chel), str(date), str(avg_rus)))
        self.db.conn.commit()

    def getUsersId(self):
        res = []
        for row in self.db.curr.execute("SELECT id FROM users").fetchall():
            res.append(row[0])
        return res

    def getUsrsByDate(self):
        rec = self.db.curr.execute("SELECT register_date, count(*) from USERS group by register_date").fetchall()
        res = []
        for row in rec:
            res.append((row[0], row[1]))
        return res

    def getSpreadVal(self, chip):
        rec = self.db.curr.execute("SELECT * FROM price_spread_stat WHERE chip = ?", (chip,)).fetchone()
        return (rec[1], rec[2])

    def getDateAndPrices(self, id, link):
        ident = self.db.curr.execute("SELECT id FROM favourites WHERE usr = ? AND link = ?", (str(id), link)).fetchone()
        self.db.curr.execute("SELECT price, fdate FROM favourites_price_changes WHERE id = ?", (str(ident[0])))
        rec = self.db.curr.fetchall()
        res_date = []
        res_price = []
        for row in rec:
            res_date.append(row[1])
            res_price.append(row[0])
        return (res_date, res_price)