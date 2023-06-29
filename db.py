import sqlite3

DB = "database.db"


class Database:
    def __init__(self):
        self.conn = None

    def get_db(self):
        if self.conn is None:
            self.conn = sqlite3.connect(DB, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close_db(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
