import sqlite3

conn = sqlite3.connect("spettri.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM bande_gruppi_funzionali")

result = cursor.fetchall()

for item in result:
    print(item)

conn.close()