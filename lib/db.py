import sqlite3
import os
import json
import pandas as pd

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

# Query al DB, NON USARE IN PRODUZIONE
def query(query):
    if query == "":
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    conn.close()

    df = pd.DataFrame(rows, columns=columns)

    return df
import sqlite3


# Query al DB per vedere tabelle e colonne
def tabelle():
    # Connessione al database SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Variabile per raccogliere i risultati
    result = ""

    # 1. Ottenere tutte le tabelle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelle = cursor.fetchall()

    # Aggiungere le tabelle alla stringa di risultato
    result += "<b>Tabelle nel database:</b><br>"
    for tabella in tabelle:
        result += f"<b>{tabella[0]}</b><br>"

        # 2. Ottenere le colonne per ciascuna tabella
        cursor.execute(f"PRAGMA table_info({tabella[0]});")
        colonne = cursor.fetchall()

        for colonna in colonne:
            result += f"  {colonna[1]} (Tipo: {colonna[2]})<br>"
        
        result += "<br>"

    # Chiudere la connessione
    conn.close()

    # Restituire il risultato come stringa
    return result
