import sqlite3
import os
import pandas as pd

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

# Query al DB per vedere tabelle e colonne
def tabelle():
    # Connessione al database SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Ottenere tutte le tabelle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelle = cursor.fetchall()

    # Chiudere la connessione
    conn.close()

    tabelle = [x for x in tabelle if x != 'sqlite_sequence' and x != 'spettri_old']

    tabelle_new = [x[0] for x in tabelle]

    # Restituire il risultato come stringa
    return tabelle_new

def colonne(nome_tabella):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({nome_tabella});")

    colonne = cursor.fetchall()

    return colonne