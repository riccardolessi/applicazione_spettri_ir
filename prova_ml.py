import pandas as pd
import numpy as np
import sqlite3
import json
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline

def calcola_similarita(molecola: int, numero_simili: int = 0, threshold: float = 0.0):
    """
    Calcola le molecole più simili a quella selezionata utilizzando metriche di similarità spettrale.
    
    Parametri:
    ----------
    molecola : int
        Indice della molecola di riferimento (deve corrispondere a un indice valido in `nomi_validi`).
    numero_simili : int, opzionale
        Numero di molecole simili da restituire. Se 0, viene utilizzato il parametro `threshold`.
    threshold : float, opzionale
        Raggio massimo di similarità per il metodo `radius_neighbors` (usato se `numero_simili` == 0).

    Ritorna:
    --------
    list[dict]
        Lista di dizionari contenenti nome, id e distanza delle molecole simili.
    """

    # --- Connessione al database ---
    with sqlite3.connect("spettri.db") as conn:
        rows = conn.execute("SELECT id, nome, dati FROM spettri").fetchall()

    df = pd.DataFrame(rows, columns=["id", "nome", "dati"])
    X, y, nomi_spettri_validi = [], [], []

    # Parsing e validazione dei dati spettrali
    for id_val, nome_val, dati_val in zip(df["id"], df['nome'], df["dati"]):
        if not dati_val:
            continue
        try:
            spettro = json.loads(dati_val)
        except json.JSONDecodeError:
            continue

        intensita = spettro.get("y")
        # Escludi record con spettro mancante o dimensione non coerente
        if intensita is None or len(intensita) != 7054:
            continue

        X.append(np.array(intensita, dtype=float))
        y.append(id_val)
        nomi_spettri_validi.append(nome_val)

    # Conversione in strutture numpy
    X = np.vstack(X)
    y = np.array(y)
    nomi_spettri_validi = np.array(nomi_spettri_validi)
    
    # Validazione parametri in ingresso
    if not (0 <= int(molecola) < len(nomi_spettri_validi)):
        raise IndexError(f"Indice molecola {molecola} fuori intervallo (0 - {len(X)-1})")

    if numero_simili == 0 and threshold == 0.0:
        raise ValueError("Devi specificare un valore per 'numero_simili' o 'threshold'.")

    # Costruzione del modello di similarità: standardizzazione + nearest neighbors
    nn_estimator = (
        NearestNeighbors(n_neighbors = numero_simili, metric="cosine")
        if numero_simili != 0
        else NearestNeighbors(radius=threshold, metric="cosine")
    )
    
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("nn", nn_estimator)
    ])

    model.fit(X)

    # Spettro della molecola di riferimento
    nuovo_spettro = X[int(molecola)].reshape(1, -1)
    print(f"Molecola di riferimento: {nomi_spettri_validi[int(molecola)]} [ID {y[int(molecola)]}]")

    # Normalizzazione prima della ricerca
    X_transf = model.named_steps["scaler"].transform(nuovo_spettro)

    # Calcolo delle similarità
    if numero_simili != 0:
        distances, indices = model.named_steps["nn"].kneighbors(X_transf)
    else:
        distances, indices = model.named_steps["nn"].radius_neighbors(X_transf)

    # Costruzione dei risultati
    risultati = [
        {
            "nome": nomi_spettri_validi[id],
            "id": int(y[id]),
            "distanza": round(float(dist), 3)
        }
        for id, dist in zip(indices[0], distances[0])
    ]

    return risultati


def get_nomi_validi() -> dict:
    """
    Estrae i nomi delle molecole con dati spettrali validi dal database.
    Filtra solo gli spettri con lunghezza coerente (7054 punti).
    """
    
    with sqlite3.connect("spettri.db") as conn:
        rows = conn.execute("SELECT nome, dati FROM spettri").fetchall()

    nomi_spettri_validi = []
    for nome, dati in rows:
        if not dati:
            continue
        try:
            spettro = json.loads(dati)
        except json.JSONDecodeError:
            continue
        intensita = spettro.get("y", None)
        if intensita is None or len(intensita) != 7054:
            continue
        nomi_spettri_validi.append(nome)

    # Mappatura indice -> nome per permettere la selezione utente
    scelte = {i: nome for i, nome in enumerate(nomi_spettri_validi)}

    return scelte
