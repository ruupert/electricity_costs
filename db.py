import sqlite3

from decorator import LogDecorator


class ElectricityDatabaseSQ(object):

    @LogDecorator()
    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile)
        self.cursor = self.conn.cursor()
        self.__exec_sql("""CREATE TABLE IF NOT EXISTS electricity (date TEXT NOT NULL, price REAL DEFAULT 0.0, kwh REAL DEFAULT 0.0);""")
        self.__exec_sql("""CREATE UNIQUE INDEX IF NOT EXISTS idx_electricity_date ON electricity (date);""")

    @LogDecorator()
    def __exec_sql(self, query, data_tuple=None):
        if data_tuple == None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, data_tuple)
        self.conn.commit()

    @LogDecorator()
    def insert_or_update(self, column, data_tuple):
        self.__exec_sql(f"""INSERT OR IGNORE INTO electricity (date) VALUES ('{data_tuple[0]}')""")
        self.__exec_sql(f"""UPDATE electricity SET {column} = '{data_tuple[1]}' WHERE date = '{data_tuple[0]}';""")

    @LogDecorator()
    def find_latest_entry(self, column):
        self.cursor.execute(f"""select date from electricity where {column} > 0.0 order by date desc limit 1;""")
        return self.cursor.fetchone()[0]

    @LogDecorator()
    def close(self):
        self.cursor.close()
        self.conn.close()
