import sqlite3
import json
import pandas as pd
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

def get_dati_spettro(filename):
    namelist = filename.split('_')
    name = namelist[2]
    
    # Veririca del tipo di prova
    if (name[:3].lower() == "std"):
        tipologia = "Standard"
    elif(name[:3].lower() == "inc"):
        tipologia = "Incognita"
    else:
        tipologia = "Sconosciuta"

    return {
        'data': namelist[1],
        'molecola': name,
        'tipologia_prova': tipologia,
        'tipologia_spettrometro': namelist[3].split('.')[0], # Splitta "ATR.dx" in "ATR"
    }

# Funzione per ottenere tutti gli spettri caricati nel db
def get_spettri():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM spettri")
    spettri = cursor.fetchall()
    conn.close()

    # Trasforma la lista di tuple in un dizionario
    result = {f"{id_}": f"{name}" for id_, name in spettri}

    return result

def get_spettro(spettro_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, dati FROM spettri WHERE id = ?", (spettro_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            spettro_data = json.loads(row[1])  # Decodifica la stringa JSON
            return {
                "nome_molecola": row[0],
                "dati_spettro": spettro_data
            }
        except json.JSONDecodeError as e:
            print(f"Errore nel decodificare i dati JSON")
            return None
    else:
        print("Nessuno spettro trovato con l'id fornito.")
        return None

# Funzione per salvare lo spettro
def save_spettro(dati_spettro):
    if not dati_spettro:
        return None

    # Serializza in JSON i dati
    try:
        dati_json = json.dumps({
            "x": dati_spettro["dati"]["x"].tolist(),
            "y": dati_spettro["dati"]["y"].tolist()
        })
    except Exception as e:
        return f"Errore nella serializzazione dei dati: {e}"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO spettri (nome, dati) VALUES(?, ?)",
    (dati_spettro["metadati"]["molecola"][3:], dati_json))

    conn.commit()
    conn.close()

    return "Molecola inserita nel database con successo"