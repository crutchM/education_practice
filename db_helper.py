import data_base
import datetime
import string
from Query import Query
from Ad import Advertisement
from user import User
class db_helper:
    def __init__(self):
        self.db = data_base.data_base()

    def addUser(self, usr):
        self.db.curr.execute("INSERT INTO users VALUES(?,?,?,?);", (str(usr.id), usr.role, usr.location, usr.regDate))
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
        self.db.curr.execute("SELECT q.vdate, count(*) FROM queries q group by q.vdate;")
        records = self.db.curr.fetchall()
        stat = dict(string, int)  # format yyyy-mm-dd
        for row in records:
            stat.update(row[0], row[1])
        return stat

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
        self.db.curr.execute("SELECT MAX(fdate) FROM favourites_price_change ")
        max_date = self.db.curr.fetchone()
        for id in list:
            self.updateOncePrice(id, self.db.curr.execute("SELECT price FROM favourites_price_change where id = ? AND fdate = ?",
                                             (str(id), max_date)).fetchone())
        self.db.conn.commit()

    def updateOncePrice(self, id, sum):
        self.db.curr.execute("UPDATE favourites set price = ? where id = ?", (str(sum), str(id)))
        self.db.conn.commit()

    def doTest(self):
        self.db.curr.execute("INSERT INTO users VALUES(?,?,?,?);", (str(123), "usr.role", "usr.location", "2021-09-09"))
        self.db.conn.commit()
        return self.db.curr.execute("SELECT * FROM users").fetchone()
    def getUser(self, id):
        self.db.curr.execute("SELECT * FROM users WHERE id = ?", (str(id),))
        res = self.db.curr.fetchone()
        return User(id=res[0], location=res[2], role=res[1], regDate=res[3])

    def getLastQuery(self, id):
        max_date = self.db.curr.execute("SELECT MAX(qdate) from queries where usr = ?", (id,)).fetchone()
        self.db.curr.execute("SELECT * FROM queries where qdate = ?", (max_date,))
        res = self.db.curr.fetchone()
        return Query(chipName=res[6], sellerRate=res[4], minCost=res[2], maxCost=res[3], sort=res[5], rad=res[1])

