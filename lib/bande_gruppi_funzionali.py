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
    cursor.execute("SELECT * from bande_gruppi_funzionali")
    bande = cursor.fetchall()
    conn.close()

    if bande:
        if need_df:
            return pd.DataFrame(bande, columns=['id', 'gruppo_funzionale', 'min', 'max'] )
        else:
            return bande
    else:
        if need_df:
            return pd.DataFrame(columns=['id', 'gruppo_funzionale', 'min', 'max'])
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

    print("bande" , bande)

    return bande

# C'è un problema che la lista id mi viene ritornata come ('2', ) e mi dà errore