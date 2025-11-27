import sqlite3

con = sqlite3.connect("optree.db")
cur = con.cursor()

res = cur.execute("SELECT * FROM Lines")

print(res.fetchall())
