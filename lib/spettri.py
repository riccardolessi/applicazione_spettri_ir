import sqlite3
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from lib import bande_gruppi_funzionali as bd

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

# Funzione per ottenere tutti gli spettri caricati nel db (solo nome)
def get_spettri():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM spettri ORDER BY nome ASC")
    spettri = cursor.fetchall()
    conn.close()

    # Trasforma la lista di tuple in un dizionario
    result = {f"{id_}": f"{name}" for id_, name in spettri}

    return result

# Funzione per ottenere un singolo spettro
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

# Renderizza il plot nella schermata di visualizzazione
def render_plot(dati, bande_selezionate = None, spettro_confronto = None):
    lista_bande = None
    if bande_selezionate:
        lista_bande = bd.get_gruppi_funzionali_selezionati(bande_selezionate)

    if not dati:
            return None  # Evita errori se il dato è nullo
        
    data = dati['dati']
    if 'x' not in data or 'y' not in data:
        return None  # Evita errori se il formato è sbagliato

    # Estrae i dati dell'asse x e y
    x = np.array(data['x'])
    y = np.array(data['y'])

    # Crea il grafico
    fig, ax = plt.subplots()
    ax.plot(x, y, label=f"{dati['metadati']['molecola'].split('/')[0]}", color="C1")
    if spettro_confronto:
        x1 = np.array(spettro_confronto["dati"]["x"])
        y1 = np.array(spettro_confronto["dati"]["y"])
        ax.plot(x1, y1, label=f"{spettro_confronto['metadati']['molecola'].split('/')[0]}", color = "C0")
    # ax.set_xlabel("Frequenza / Lunghezza d'onda")
    # ax.set_ylabel("Intensità")

    if lista_bande:
        for banda_singola in lista_bande:
            ax.axvspan(banda_singola[2], banda_singola[3], color="lightgreen", alpha=0.5)

    if not spettro_confronto:
        ax.set_title(f"Spettro della molecola: {dati['metadati']['molecola'].split('/')[0]}")
    else: ax.set_title(f"Spettro delle molecole: {dati['metadati']['molecola'].split('/')[0]} - {spettro_confronto['metadati']['molecola'].split('/')[0]}")
    ax.legend()
    ax.grid()

    ax.invert_xaxis()

    return fig