import sqlite3
import json
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

def get_dati_spettro(filename):
    namelist = filename.split('_')
    name = namelist[2]
    
    # Veririca del tipo di prova
    if (name[:3].lower() == "std"):
        tipologia = "STD"
    elif(name[:3].lower() == "inc"):
        tipologia = "INC"
    else:
        tipologia = "Sconosciuta"
        return None

    data = {
        'data': namelist[1],
        'molecola': name[3:],
        'tipologia_prova': tipologia,
        'tipologia_spettrometro': namelist[3].split('.')[0], # Splitta "ATR.dx" in "ATR"
    }

    nome_molecola_db = nome_spettro(data)
    data['nome_molecola_db'] = nome_molecola_db

    return data

# Funzione per ottenere tutti gli spettri caricati nel db
def get_spettri():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM spettri ORDER BY nome ASC")
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
                "metadati": {
                    "molecola": row[0]
                },
                "dati": spettro_data
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
    cursor.execute("INSERT INTO spettri (nome, data_spettro, tipologia_spettrometro, tipologia_prova, dati) VALUES(?, ?, ?, ?, ?)",
    (dati_spettro["metadati"]["nome_molecola_db"], dati_spettro["metadati"]["data_ora"], dati_spettro["metadati"]["tipologia_spettrometro"], dati_spettro["metadati"]["tipologia_prova"], dati_json))

    conn.commit()
    conn.close()

    return "Molecola inserita nel database con successo"


# Funzione per evitare di caricare duplicati nel DB
def check_duplicati(nome, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM spettri WHERE nome = ? AND data_spettro = ?", (nome, data))
    result = cursor.fetchall()
    conn.close()

def render_plot(dati):
    if not dati:
            return None  # Evita errori se il dato è nullo
        
    data = dati['dati']
    if 'x' not in data or 'y' not in data:
        return None  # Evita errori se il formato è sbagliato

    # Estrae i dati dell'asse x e y
    x = np.array(data['x'])
    y = np.array(data['y'])

    # Crea il grafico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, label=f"{dati['metadati']['molecola']}", color="blue")
    ax.set_xlabel("Frequenza / Lunghezza d'onda")
    ax.set_ylabel("Intensità")
    ax.set_title(f"Spettro della molecola: {dati['metadati']['molecola']}")
    ax.legend()
    ax.grid()

    ax.invert_xaxis()

    return fig