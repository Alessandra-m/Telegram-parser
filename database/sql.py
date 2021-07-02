import sqlite3

conn = sqlite3.connect(r'database/bd.db')

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS database(
   userid INT PRIMARY KEY,
   name TEXT,
   sentence TEXT,
   price INT,
   URL TEXT,
   id INT);
""")

conn.commit()

