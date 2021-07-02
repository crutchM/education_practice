import sqlite3

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
        FOREIGN KEY (user) REFERENCES users(id)     
    );
""")

conn.commit()

def addUser(user):
    curr.execute("INSERT INTO users VALUES(?,?,?,?,?);", user)
    conn.commit()

def addToFavourite(advertisement):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?,?);", advertisement)
    conn.commit()

def addToQueriesHistory(query):
    curr.execute("INSERT INTO favourites VALUES(?,?,?,?,?,?,?,?);", query)
    conn.commit()