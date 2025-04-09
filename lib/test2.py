import sqlite3
import os
import pandas as pd

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

# Query al DB per vedere i gruppi funzionali
def gruppi_funzionali():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gruppi_funzionali")
    row = cursor.fetchall()
    conn.close()

    output = {banda[0]: banda[1] for banda in row}

    return output

def fonti():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fonti")
    row = cursor.fetchall()
    conn.close()

    output = {fonte[0]: fonte[1] for fonte in row}

    return output

def salva_fonte(nome_fonte):

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fonti (nome) VALUES(?)", (nome_fonte, ))
        
        conn.commit()
        conn.close()

        return "success"

    except sqlite3.Error as e:
        return f"Errore: {e}"
    
def salva_gruppo_funzionale(nome_gruppo, smiles):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if smiles != "":
            cursor.execute("INSERT INTO gruppi_funzionali (gruppo_funzionale, smile_gruppo) VALUES (?, ?)", (nome_gruppo, smiles))
        else:
            cursor.execute("INSERT INTO gruppi_funzionali (gruppo_funzionale) VALUES (?)", (nome_gruppo, ))

        conn.commit()
        conn.close()

        return "success"

    except sqlite3.Error as e:
        return f"Errore: {e}"
    
def salva_banda_gruppo_funzionale(nome_banda, min, max, id_gruppo_funzionale, fonte_banda):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bande_gruppi_funzionali
            (gruppo_funzionale, min, max, id_gruppo, fonte_bande)
            VALUES (?, ?, ?, ?, ?)
        """, (nome_banda, min, max, id_gruppo_funzionale, fonte_banda))

        conn.commit()
        conn.close()

        return "success"

    except sqlite3.Error as e:
        return f"Errore: {e}"