import sqlite3

with open("tables.sql") as sql_file:
    sql_string = sql_file.read()
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    # ONE TIME SETUP
    cur.execute(sql_string)
    con.commit()
