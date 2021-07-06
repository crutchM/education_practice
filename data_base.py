import sqlite3
import string
from Query import Query
from Ad import Advertisement

conn = sqlite3.connect('users.sql', check_same_thread=False)

curr = conn.cursor()

curr.execute("""
    CREATE TABLE IF NOT EXISTS  users(
        id INT PRIMARY KEY,
        role TEXT NOT NULL,
        location TEXT NOT NULL,
        register_date DATE
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS favourites(
        
        usr INT,
        link TEXT NOT NULL,
        price INT,
        name TEXT,
        FOREIGN KEY (usr) REFERENCES users(id)
    ); 
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS queries(
        usr INT,
        filter_radius INT,
        filter_min_price INT,
        filter_max_price INT,
        filter_saller_rate DOUBLE,
        sort_type INT,
        query TEXT, 
        qdate DATE,
        FOREIGN KEY (usr) REFERENCES users(id)     
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS avg_price_stat(
        chip_name TEXT PRIMARY KEY,
        avg_price_chel INT,
        cdate DATE,
        avg_price_rus INT
    );
    """)

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS cardList(
        card_name TEXT,
        usr INT,
        FOREIGN KEY (usr) REFERENCES users(id),
        FOREIGN KEY (card_name) REFERENCES price_spread_stat(chip),
        FOREIGN KEY (card_name) REFERENCES avg_price_stat(chip_name),
        CONSTRAINT cl_pk PRIMARY KEY (card_name, usr)
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS price_spread_stat(
        chip TEXT PRIMARY KEY,
        values_rus TEXT,
        values_chel TEXT
    );
""")

conn.commit()

def addUser(usr):
    curr.execute("INSERT INTO users VALUES(?,?,?,?,?);", (str(usr.id), usr.role, usr.location, usr.reg_date, None))
    conn.commit()

def isUsrExists(user):
    curr.execute("SELECT * FROM users WHERE id =" + str(user) + ";")
    return curr.fetchone() is not None

def addToFavourite(advertisement, usrid):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?);", (str(usrid), advertisement.link, advertisement.cost, advertisement.name))
    conn.commit()

def addToQueriesHistory(query, id, date):
    curr.execute("INSERT INTO queries VALUES(?,?,?,?,?,?,?,?);", (id, query.rad, query.minCost, query.maxCost, query.sellerRate, query.sort, query.chipName, date))
    conn.commit()

def getFavourites(userid):
    curr.execute("SELECT * FROM FAVOURITES WHERE usr = " + str(userid) + ";" )
    records = curr.fetchall()
    recordslist = []
    for row in records:
        recordslist.append(Advertisement(row[3], row[4], row[2]))
    return recordslist

def getQuriesHistory(userid):
    curr.execute("SELECT * FROM queries WHERE usr = ?;", (str(userid),))
    records = curr.fetchall()
    recordslist = []
    for row in records:
        recordslist.append(Query(chipName=row[6], sort=row[5], sellerRate=row[4], rad=row[1], minCost=row[2], maxCost=row[3]))
    return recordslist

def getVisits():
    curr.execute("SELECT q.vdate, count(*) FROM queries q group by q.vdate;")
    records = curr.fetchall()
    stat = dict(string, int) #format yyyy-mm-dd
    for row in records:
        stat.update(row[0], row[1])
    return stat

def getLocation(id):
    curr.execute("SELECT location FROM users WHERE id = ?;", (str(id),))
    return curr.fetchone()

def setValToSpread(chip, values_rus, values_chel):
    if curr.execute("SELECT * FROM price_spread_stat p WHERE p.chip = ?", (chip,)).fetchone() is None:
        curr.execute("INSERT INTO price_spread_stat VALUES (?,?,?)", (chip, values_rus, values_chel))
        conn.commit()
    else: curr.execute("UPDATE price_spread_stat set  values_rus = ?, values_chel = ? WHERE chip = ?", (values_rus, values_chel, chip))
    conn.commit()

def getPriceAndDateList(chip):
    curr.execute("SELECT * FROM avg_price_stat WHERE chip_name = ?", (chip,))
    rec = curr.fetchall()
    avg_chel = []
    avg_rus = []
    date = []
    for row in rec:
        avg_chel.append(row[1])
        avg_rus.append(row[3])
        date.append(row[2])
    return (avg_rus, avg_chel, date)

def addCard(user, card):
    curr.execute("INSERT INTO cardList VALUES (?,?)", (card, user))
    conn.commit()