import sqlite3

DATABASE_NAME = "halts.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS halts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            company TEXT,
            reason TEXT,
            halt_time TEXT,
            halt_date TEXT,
            market TEXT,
            timestamp TEXT UNIQUE
        )
    """)

    connection.commit()
    connection.close()