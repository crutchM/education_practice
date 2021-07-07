
import sqlite3

class data_base:
    def __init__(self):
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.curr = self.conn.cursor()
        self.createDB()


    def createDB(self):
        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS  users(
                id INT PRIMARY KEY,
                role TEXT NOT NULL,
                location TEXT NOT NULL,
                register_date DATE
            );
        """)

        self.conn.commit()

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS favourites(
                id INTEGER PRIMARY KEY, 
                usr INT,
                link TEXT NOT NULL,
                price INT,
                name TEXT,
                FOREIGN KEY (usr) REFERENCES users(id)
            ); 
        """)

        self.conn.commit()

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS queries(
                usr INT,
                filter_radius INT,
                filter_min_price INT,
                filter_max_price INT,
                filter_saller_rate DOUBLE,
                sort_type INT,
                query TEXT, 
                qdate DATETIME,
                FOREIGN KEY (usr) REFERENCES users(id)     
            );
        """)

        self.conn.commit()

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS avg_price_stat(
                chip_name TEXT PRIMARY KEY,
                avg_price_chel INT,
                cdate DATE,
                avg_price_rus INT
            );
            """)

        self.conn.commit()

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS cardList(
                card_name TEXT,
                usr INT,
                FOREIGN KEY (usr) REFERENCES users(id),
                FOREIGN KEY (card_name) REFERENCES price_spread_stat(chip),
                FOREIGN KEY (card_name) REFERENCES avg_price_stat(chip_name),
                CONSTRAINT cl_pk PRIMARY KEY (card_name, usr)
            );
        """)

        self.conn.commit()

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS price_spread_stat(
                chip TEXT PRIMARY KEY,
                values_rus TEXT,
                values_chel TEXT
            );
        """)

        self.conn.commit()

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS favourites_price_change(
                favourite INTEGER,
                price INTEGER,
                fdate DATE,
                FOREIGN KEY(favourite) REFERENCES favourites(id)
            );
        """)
        self.conn.commit()
