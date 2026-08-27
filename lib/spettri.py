import sqlite3
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from lib import bande_gruppi_funzionali as bd
from pathlib import Path
from contextlib import closing

# Path del DB
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

def _check_db() -> None:
    """Verifica che il file del database esista"""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database non trovato: {db_path}")

def get_spettri() -> dict[str, str]:
    """
    Recupera tutti gli spettri dal database.
    Ritorna un dizionario {id: nome} ordinato per nome.
    """
    _check_db()

    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, nome FROM spettri ORDER BY nome ASC")
            spettri = cursor.fetchall()

    result = {f"{id_}": f"{name}" for id_, name in spettri}
    return result


def get_spettri_con_smiles() -> list[tuple]:
    """
    Recupera tutti gli spettri con il loro SMILES dal database.
    Ritorna una lista di tuple (id, nome, smiles) ordinata per nome.
    """
    _check_db()

    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, nome, smiles FROM spettri ORDER BY nome ASC")
            return cursor.fetchall()
    
# # Funzione per ottenere tutti gli spettri caricati nel db (solo nome)
# def get_spettri(need_smiles = False):
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
    
#     if need_smiles:
#         cursor.execute("SELECT id, nome, smiles FROM spettri ORDER BY nome ASC")
#     else:
#         cursor.execute("SELECT id, nome FROM spettri ORDER BY nome ASC")
    
#     spettri = cursor.fetchall()
#     conn.close()

#     if need_smiles:
#         return spettri
    
#     # Trasforma la lista di tuple in un dizionario
#     result = {f"{id_}": f"{name}" for id_, name in spettri}

#     return result

# # Funzione per ottenere un singolo spettro
# def get_spettro(spettro_id: int | str) -> dict | None:
#     """
#     Recupera un singolo spettro dal database tramite ID.
#     Ritorna un dizionario con metadati, dati e fonte, oppure None se non trovato.

#     Raises:
#         FileNotFoundError: se il database non esiste
#         ValueError: se i dati JSON dello spettro sono corrotti
#     """
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT spettri.nome, spettri.dati, fonti.nome FROM spettri LEFT JOIN fonti on fonti.id = spettri.fonte_spettri WHERE spettri.id = ?;", (spettro_id,))
#     row = cursor.fetchone()
#     conn.close()

#     if row:
#         try:
#             spettro_data = json.loads(row[1])  # Decodifica la stringa JSON
#             return {
#                 "metadati": {
#                     "molecola": row[0]
#                 },
#                 "dati": spettro_data,
#                 "fonte_spettro": row[2]
#             }
#         except json.JSONDecodeError as e:
#             print(f"Errore nel decodificare i dati JSON")
#             return None
#     else:
#         print("Nessuno spettro trovato con l'id fornito.")
#         return None

def get_spettro(spettro_id: int | str) -> dict | None:
    """
    Recupera un singolo spettro dal database tramite ID.
    Ritorna un dizionario con metadati, dati e fonte, oppure None se non trovato.
    
    Raises:
        FileNotFoundError: se il database non esiste
        ValueError: se i dati JSON dello spettro sono corrotti
    """
    _check_db()

    query = """
        SELECT spettri.nome, spettri.dati, fonti.nome
        FROM spettri
        LEFT JOIN fonti on fonti.id = spettri.fonte_spettri
        WHERE spettri.id = ?
    """

    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query, (spettro_id,))
            row = cursor.fetchone()

    if row is None:
        raise ValueError(f"Nessuno spettro trovato con id: {spettro_id}")
    
    try:
        spettro_data = json.loads(row[1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Dati JSON corrotti per lo spettro con id {spettro_id}: {e}")
    
    return {
        "metadati": {
            "molecola": row[0]
        },
        "dati": spettro_data,
        "fonte_spettro": row[2]
    }

# Renderizza il plot nella schermata di visualizzazione
# def render_plot(dati, bande_selezionate = None, spettro_confronto = None, colore_molecola = "k", colore_standard = "C0", larghezza_bande_singole = None):
#     lista_bande = None
#     if bande_selezionate:
#         lista_bande = bd.get_gruppi_funzionali_selezionati(bande_selezionate)
#     # Ciclo for per modificare le bande singole (quelle larghe 2)
#     # per allargarle come da input slider utente
#     if larghezza_bande_singole and bande_selezionate:
#         lista_bande_array = []
#         for banda in lista_bande:
#             banda_array = []
#             for x in banda:
#                 banda_array.append(x)
            
#             banda_array[3] = banda_array[3] + larghezza_bande_singole - 1
#             banda_array[2] = banda_array[2] - larghezza_bande_singole + 1
            
#             lista_bande_array.append(banda_array)
        
#         lista_bande = lista_bande_array
#         print(lista_bande)

#     if not dati:
#             return None  # Evita errori se il dato è nullo
        
#     data = dati['dati']
#     if 'x' not in data or 'y' not in data:
#         return None  # Evita errori se il formato è sbagliato

#     # Estrae i dati dell'asse x e y
#     x = np.array(data['x'])
#     y = np.array(data['y'])

#     # Crea il grafico
#     fig, ax = plt.subplots()
#     ax.plot(x, y, label=f"{dati['metadati']['molecola']}", color=colore_molecola)
#     if spettro_confronto:
#         x1 = np.array(spettro_confronto["dati"]["x"])
#         y1 = np.array(spettro_confronto["dati"]["y"])
#         ax.plot(x1, y1, label=f"{spettro_confronto['metadati']['molecola']}", color = colore_standard)
#     # ax.set_xlabel("Frequenza / Lunghezza d'onda")
#     # ax.set_ylabel("Intensità")

#     if lista_bande:
#         for banda_singola in lista_bande:
#             ax.axvspan(banda_singola[2], banda_singola[3], color="lightgreen", alpha=0.5)

#     if not spettro_confronto:
#         ax.set_title(f"Spettro della molecola: {dati['metadati']['molecola'].split('/')[0]}")
#     else: ax.set_title(f"Spettro delle molecole: {dati['metadati']['molecola'].split('/')[0]} - {spettro_confronto['metadati']['molecola'].split('/')[0]}")
#     ax.legend()
#     ax.grid()

#     ax.invert_xaxis()

#     return fig

def render_plot(
    dati: dict,
    bande_selezionate: list | None = None,
    spettro_confronto: dict | None = None,
    colore_molecola: str = "k",
    colore_standard: str = "C0",
    larghezza_bande_singole: int | None = None
) -> plt.Figure | None:
    """
    Genera il grafico di uno spettro IR.
    
    Args:
        dati: dizionario con chiavi 'dati' (x, y) e 'metadati' (molecola)
        bande_selezionate: lista di gruppi funzionali da evidenziare
        spettro_confronto: dizionario opzionale con lo stesso formato di dati
        colore_molecola: colore matplotlib per lo spettro principale
        colore_standard: colore matplotlib per lo spettro di confronto
        larghezza_bande_singole: allargamento opzionale delle bande
    
    Returns:
        Figure matplotlib oppure None se i dati sono invalidi
    
    Raises:
        KeyError: se il formato di dati o spettro_confronto è incorretto
    """
    if not dati:
        return None

    data = dati.get("dati", {})
    if "x" not in data or "y" not in data:
        return None

    lista_bande = _get_bande(bande_selezionate, larghezza_bande_singole)

    fig, ax = plt.subplots()
    _plot_spettro(ax, data, dati["metadati"]["molecola"], colore_molecola)

    if spettro_confronto:
        _plot_spettro(ax, spettro_confronto["dati"], spettro_confronto["metadati"]["molecola"], colore_standard)

    if lista_bande:
        _plot_bande(ax, lista_bande)

    ax.set_title(_build_titolo(dati, spettro_confronto))
    ax.legend()
    ax.grid()
    ax.invert_xaxis()

    return fig


# --- Helper privati ---

def _get_bande(
    bande_selezionate: list | None,
    larghezza_bande_singole: int | None
) -> list | None:
    """Recupera e opzionalmente allarga le bande selezionate."""
    if not bande_selezionate:
        return None

    lista_bande = bd.get_gruppi_funzionali_selezionati(bande_selezionate)

    if larghezza_bande_singole:
        lista_bande = [
            _allarga_banda(banda, larghezza_bande_singole)
            for banda in lista_bande
        ]

    return lista_bande


def _allarga_banda(banda: list, larghezza: int) -> list:
    """Allarga una singola banda in base al valore dello slider."""
    banda = list(banda)
    banda[2] = banda[2] - larghezza + 1
    banda[3] = banda[3] + larghezza - 1
    return banda


def _plot_spettro(ax: plt.Axes, data: dict, label: str, colore: str) -> None:
    """Aggiunge uno spettro al grafico."""
    x = np.array(data["x"])
    y = np.array(data["y"])
    ax.plot(x, y, label=label, color=colore)


def _plot_bande(ax: plt.Axes, lista_bande: list) -> None:
    """Evidenzia le bande sul grafico."""
    for banda in lista_bande:
        ax.axvspan(banda[2], banda[3], color="lightgreen", alpha=0.5)


def _build_titolo(dati: dict, spettro_confronto: dict | None) -> str:
    """Costruisce il titolo del grafico."""
    nome_principale = dati["metadati"]["molecola"].split("/")[0]

    if spettro_confronto:
        nome_confronto = spettro_confronto["metadati"]["molecola"].split("/")[0]
        return f"Spettro delle molecole: {nome_principale} - {nome_confronto}"

    return f"Spettro della molecola: {nome_principale}"