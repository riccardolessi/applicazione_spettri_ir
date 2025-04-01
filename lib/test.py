import sqlite3
import json
import os
import numpy as np
import matplotlib.pyplot as plt

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
# cursor.execute("SELECT id, nome FROM spettri ORDER BY nome ASC")
# spettri = cursor.fetchall()
# conn.close()

def get_spettro(spettro_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, dati, smiles FROM spettri WHERE id = ?;", (spettro_id,))
    row = cursor.fetchone()
    conn.close()

    return row

# Renderizza il plot nella schermata di visualizzazione
def render_plot(dati, bande_selezionate = []):
    if not dati:
            return None  # Evita errori se il dato è nullo
    
    spettro_data = json.loads(dati)
        
    if 'x' not in spettro_data or 'y' not in spettro_data:
        print("ERROREEEEE!!!!!!!!!!!!!")
        return None  # Evita errori se il formato è sbagliato

    # Estrae i dati dell'asse x e y
    x = np.array(spettro_data['x'])
    y = np.array(spettro_data['y'])

    # Crea il grafico
    fig, ax = plt.subplots()
    ax.plot(x, y, label="Test")
    

    if bande_selezionate:
        ax.axvspan(bande_selezionate[0], bande_selezionate[1], color="lightgreen", alpha=0.5)

    ax.legend()
    ax.grid()

    ax.invert_xaxis()

    return fig

def pippo(id_spettro, banda):
    molecola = get_spettro(id_spettro)
    plot = render_plot(molecola[1], banda)

    return plot
