import os
import sqlite3

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

def get_fonti():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM fonti ORDER BY nome ASC")
    fonti = cursor.fetchall()
    conn.close()

    return fonti