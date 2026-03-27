import sqlite3


def connect_db():

    conn = sqlite3.connect("user_data.db")
    return conn


def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preferences(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        semester TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_preferences(email, semester):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO preferences(email, semester) VALUES(?,?)",
        (email, semester)
    )

    conn.commit()
    conn.close()
    