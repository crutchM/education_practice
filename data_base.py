import sqlite3
import string

from adverticement import Adverticement
from query import Query

conn = sqlite3.connect('users.sql', check_same_thread=False)

curr = conn.cursor()

curr.execute("""
    CREATE TABLE IF NOT EXISTS  users(
        id INT PRIMARY KEY,
        role TEXT NOT NULL,
        location TEXT NOT NULL,
        register_date DATE,
        last_query INT,
        FOREIGN KEY (last_query) REFERENCES queries(id)
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS favourites(
        id INT PRIMARY KEY ,
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
        id INT PRIMARY KEY,
        usr INT,
        filter_radius INT,
        filter_min_price INT,
        filter_max_price INT,
        filter_saller_rate DOUBLE,
        sort_type INT,
        query TEXT, 
        vdate DATE,
        FOREIGN KEY (usr) REFERENCES users(id)     
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS chipStat(
        chip_name TEXT PRIMARY KEY,
        avg_price_chel INT,
        cdate DATE,
        avg_price_rus INT
    );
    """)



conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS cardList(
        id INTEGER PRIMARY KEY,
        card_name TEXT,
        usr INT,
        FOREIGN KEY (usr) REFERENCES users(id)
    )
""")
def addUser(user):
    curr.execute("INSERT INTO users VALUES(?,?,?,?);", user.id, user.role, user.location, user.reg_date)
    conn.commit()

def addToFavourite(advertisement):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?,?);", advertisement)
    conn.commit()

def addToQueriesHistory(query):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?,?,?,?,?);", query)
    conn.commit()

def getFavourites(userid):
    curr.execute("SELECT * FROM FAVOURITES WHERE usr = " + str(userid) + ";" )
    records = curr.fetchall()
    recordslist = []
    for row in records:
        recordslist.append(Adverticement(row[3], row[4], row[2]))
    return recordslist

def getQuriesHistory(userid):
    curr.execute("SELECT * FROM queries WHERE id = ?;", userid)
    records = curr.fetchall()
    recordslist = []
    for row in records:
        recordslist.append(Query(row[2], row[7], row[5], row[3], row[4], row[6]))
    return recordslist

def getVisits():
    curr.execute("SELECT q.vdate, count(*) FROM queries q group by q.vdate;")
    records = curr.fetchall()
    stat = dict(string, int) #format yyyy-mm-dd
    for row in records:
        stat.update(row[0], row[1])
    return stat

def getLocation(id):
    curr.execute("SELECT location FROM users WHERE id = ?;", str(id))
    return curr.fetchone()
