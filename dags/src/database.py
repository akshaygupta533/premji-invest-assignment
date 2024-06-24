import os
import sqlite3
from datetime import datetime

from pytz import timezone

# Database file path
db_file = "dags/database.db"


class DataBase:
    def __init__(self):
        # Check if the database file exists, if not, create one
        if not os.path.exists(db_file):
            print(f"Database file '{db_file}' does not exist. Creating a new one...")
            self.conn = sqlite3.connect(db_file)
            cursor = self.conn.cursor()
            # Create a table
            cursor.execute(
                """
                CREATE TABLE scores (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    url TEXT NOT NULL,
                    score REAL NOT NULL
                )
            """
            )
            self.conn.commit()
            cursor.close()
            print(f"Database file '{db_file}' created successfully.")
        else:
            self.conn = sqlite3.connect(db_file)
            print(f"Database file '{db_file}' already exists.")

    # Function to insert data into the database
    def insert_data(self, data):
        cursor = self.conn.cursor()
        for row in data:
            cursor.execute(
                """
                INSERT INTO scores (timestamp, ticker, url, score)
                VALUES (?, ?, ?, ?)
            """,
                (
                    datetime.strftime(
                        datetime.now(timezone("Asia/Kolkata")), "%Y-%m-%d %H:%M:%S"
                    ),
                    row["ticker"],
                    row["url"],
                    row["score"]
                ),
            )
        self.conn.commit()
        cursor.close()

    def close_conn(self):
        self.conn.close()
