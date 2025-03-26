import sqlite3
import os
import pandas as pd

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

# Funzione per ritornare tutti i gruppi funzionali presenti nel DB
# need_df serve per visualizzare la tabella nel frontend ed avere i dati nel formato
# corretto per visualizzare le bande nel grafico
def get_gruppi_funzionali(need_df):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""SELECT 
        bande_gruppi_funzionali.id, 
        bande_gruppi_funzionali.gruppo_funzionale,
        bande_gruppi_funzionali.min,
        bande_gruppi_funzionali.max,
        gruppi_funzionali.gruppo_funzionale,
        fonti.nome
        FROM bande_gruppi_funzionali
        JOIN gruppi_funzionali ON bande_gruppi_funzionali.id_gruppo = gruppi_funzionali.id
        JOIN fonti ON bande_gruppi_funzionali.fonte_bande = fonti.id
        """)
    bande = cursor.fetchall()
    conn.close()

    if bande:
        if need_df:
            return pd.DataFrame(bande, columns=['id', 'nome', 'min', 'max', 'gruppo funzionale', "fonte"] )
        else:
            return bande
    else:
        if need_df:
            return pd.DataFrame(columns=['id', 'nome', 'min', 'max', 'gruppo funzionale', "fonte"])
        else:
            return bande

def get_gruppi_funzionali_selezionati(lista_id):
    # Creo id_values per convertire un tuple in list
    id_values = []

    for id in lista_id:
        id_values.append(id)
    
    # Generare i segnaposto per la query (?, ?, ?)
    placeholders = ','.join(['?'] * len(id_values))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM bande_gruppi_funzionali WHERE id IN ({placeholders})", id_values)
    bande = cursor.fetchall()
    conn.close()
    
    return bande

def get_gruppi_new():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * from gruppi_funzionali ORDER BY gruppo_funzionale ASC")
    gruppi_funzionali = cursor.fetchall()
    conn.close()

    return gruppi_funzionali

def get_gruppi_funzionali_selezionati_new(lista_id):
    # Creo id_values per convertire un tuple in list
    id_values = []

    for id in lista_id:
        id_values.append(id)
    
    # Generare i segnaposto per la query (?, ?, ?)
    placeholders = ','.join(['?'] * len(id_values))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM bande_gruppi_funzionali WHERE id_gruppo IN ({placeholders}) ORDER BY gruppo_funzionale ASC", id_values)
    bande = cursor.fetchall()
    conn.close()
    
    output = {banda[0]: banda[1] for banda in bande}

    return output