import sqlite3
import os
from database_interface import DatabaseInterface


class SQLiteHandler(DatabaseInterface):

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'db', 'listing_cache.db')

        if not os.path.exists(self.db_path):
            self.create_database()
        else:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

    def create_database(self):
        """
        If database file does not exist, create SQLite database in db directory

        :return:
            None
        """

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create cache table
        self.cursor.execute("""CREATE TABLE listings (
                id INTEGER PRIMARY KEY,
                model TEXT NOT NULL,
                price INTEGER NOT NULL
            )""")

        # Create watchlist
        self.cursor.execute("""CREATE TABLE watchlist (
                id INTEGER PRIMARY KEY,
                model TEXT,
                price INTEGER
            )""")

        # Create model catalog
        self.cursor.execute("""CREATE TABLE catalog (
                model TEXT PRIMARY KEY
            )""")

        self.conn.commit()

    def get_all_from_table(self, table: str):
        # Query listings database
        self.cursor.execute(f"SELECT * FROM {table}")

        return self.cursor.fetchall()

    def clear_catalog(self):
        self.cursor.execute(f"DELETE FROM catalog")
        self.conn.commit()

    def insert_listing(self, id_num: int, model: str, price: int) -> bool:
        insert_query = "INSERT OR REPLACE INTO listings (id, model, price) VALUES (?, ?, ?)"
        dup_query = "SELECT * FROM listings WHERE id = ?"

        self.cursor.execute(dup_query, (id_num,))
        row = self.cursor.fetchone()
        if row is None or row[2] != price:
            self.cursor.execute(insert_query, (id_num, model, price))
            self.conn.commit()
            return True
        return False

    def delete_listing(self, id_num: int):
        delete_query = "DELETE FROM listings WHERE id = ?"
        self.cursor.execute(delete_query, (id_num,))
        self.conn.commit()

    def search_watchlist(self, id_num: int) -> tuple[int, str, int]:
        dup_query = "SELECT * FROM watchlist WHERE id = ?"
        self.cursor.execute(dup_query, (id_num,))
        return self.cursor.fetchone()

    def insert_watchlist(self, id_num: int, model: str, price: int):
        insert_query = "INSERT OR REPLACE INTO watchlist (id, model, price) VALUES (?, ?, ?)"
        dup_query = "SELECT * FROM watchlist WHERE id = ?"

        self.cursor.execute(dup_query, (id_num,))
        row = self.cursor.fetchone()
        if row is None or row[2] != price:
            self.cursor.execute(insert_query, (id_num, model, price))
            self.conn.commit()
        else:
            raise Exception("Item already watched")

    def remove_from_watchlist(self, id_num: int):
        delete_query = "DELETE FROM watchlist WHERE id = ?"

        if self.search_watchlist(id_num) is not None:
            self.cursor.execute(delete_query, (id_num,))
            self.conn.commit()
        else:
            raise Exception("Item not in watchlist")

    def insert_model(self, model: str) -> bool:
        insert_query = "INSERT INTO catalog VALUES (?)"
        dup_query = "SELECT COUNT(*) FROM catalog WHERE model = ?"

        self.cursor.execute(dup_query, (model,))
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(insert_query, (model,))
            self.conn.commit()
            return True
        return False

    def delete_model(self, model: str):
        delete_query = "DELETE FROM watchlist WHERE model = ?"
        self.cursor.execute(delete_query, (model,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
