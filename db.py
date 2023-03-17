import sqlite3

class ElectricityDatabase:
    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile)
        self.cursor = self.conn.cursor()

        self.__exec_sql("""CREATE TABLE IF NOT EXISTS electricity (date TEXT NOT NULL, price REAL, kwh REAL);""")
        self.__exec_sql("""CREATE UNIQUE INDEX IF NOT EXISTS idx_electricity_date ON electricity (date);""")

    def __exec_sql(self, query, data_tuple=None):
        if data_tuple == None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, data_tuple)
        self.conn.commit()

    def insert_or_update(self, column, data_tuple):
        
        self.__exec_sql(f"""INSERT OR IGNORE INTO electricity (date) VALUES ('{data_tuple[0]}')""")
        self.__exec_sql(f"""UPDATE electricity SET {column} = '{data_tuple[1]}' WHERE date = '{data_tuple[0]}';""")

        #self.__exec_sql(f"""REPLACE INTO electricity (date, {column}) VALUES (?, ?);""", data_tuple)

    def close(self):
        self.cursor.close()
        self.conn.close()

