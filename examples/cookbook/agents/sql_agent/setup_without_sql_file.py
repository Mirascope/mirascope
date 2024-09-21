import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()
# ONE TIME SETUP
cur.execute("""
    CREATE TABLE ReadingList (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Not Started', 'In Progress', 'Complete')),
        rating INTEGER CHECK(rating BETWEEN 1 AND 5)
    )
""")
con.commit()
