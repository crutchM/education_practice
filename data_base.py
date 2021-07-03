import sqlite3
from adverticement import Adverticement
from query import Query

conn = sqlite3.connect('users.sql', check_same_thread=False)

curr = conn.cursor()

curr.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INT PRIMARY KEY,
        role TEXT NOT NULL,
        location TEXT NOT NULL,
        register_date DATETIME,
        last_query INT,
        FOREIGN KEY (last_query) REFERENCES queries(id)
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS favourites(
        id INT PRIMARY KEY,
        user INT,
        link TEXT NOT NULL,
        price INT,
        name TEXT,
        FOREIGN KEY (user) REFERENCES users(id)
    ); 
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS queries(
        id INT PRIMARY KEY,
        user INT,
        filter_radius INT,
        filter_min_price INT,
        filter_max_price INT,
        filter_saller_rate DOUBLE,
        sort_type INT,
        query TEXT, 
        vdate DATE,
        FOREIGN KEY (user) REFERENCES users(id)     
    );
""")

conn.commit()

curr.execute("""
    CREATE TABLE IF NOT EXISTS chipStat(
        chip_name TEXT PRIMARY KEY,
        region TEXT,
        avg_price INT,
        cdate DATE
    )""")

def addUser(user):
    curr.execute("INSERT INTO users VALUES(?,?,?,?,?);", user)
    conn.commit()

def addToFavourite(advertisement):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?,?);", advertisement)
    conn.commit()

def addToQueriesHistory(query):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?,?,?,?,?);", query)
    conn.commit()

def getFavourites(userid):
    curr.execute("SELECT * FROM FAVOURITES WHERE user = ?;", userid)
    records = curr.fetchall()
    recordslist = list(Adverticement)
    for row in records:
        recordslist.append(Adverticement(row[3], row[4], row[2]))
    return recordslist

def getQuriesHistory(userid):
    curr.execute("SELECT * FROM queries WHERE id = ?;", userid)
    records = curr.fetchall()
    recordslist = list(Query)
    for row in records:
        recordslist.append(Query(row[2], row[7], row[5], row[3], row[4], row[6]))
    return recordslist

def getVisits(date):
    curr.execute("SELECT id FROM queries where  CAST(strftime(%s, vdate) AS INTEGER ) = CAST(strftime(%s, ?) AS INTEGER );", date)
    i = 0
    records = curr.fetchall()
    for row in records:
        i += 1
    return i