import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
import sqlite3
import json

# ==============================
# 1. Connessione al DB
# ==============================
conn = sqlite3.connect("spettri.db")
cursor = conn.cursor()

query = "SELECT id, nome, dati FROM spettri"
rows = cursor.execute(query).fetchall()
conn.close()

# ==============================
# 2. Caricamento dati
# ==============================
df = pd.DataFrame(rows, columns=["id", "nome", "dati"])
X = []
y = []

nomi_validi = []

for id_val, nome_val, dati_val in zip(df["id"], df['nome'], df["dati"]):

    if not dati_val:
        print("Stringa vuota")
        continue

    try:
        spettro_dict = json.loads(dati_val)
    except json.JSONDecodeError:
        print("Errore decodifica JSON")
        continue

    intensita = spettro_dict.get("y", None)
    molecola = id_val
    
    if intensita is None:
        print("Dati mancanti:", id_val)
        continue

    if len(intensita) != 7054:  # tieni solo quelli completi
        continue
    
    intensita = np.array(intensita, dtype=float)  # assicura array numerico
    X.append(intensita)
    y.append(molecola)
    nomi_validi.append(nome_val)

# trasformo in array 2D
X = np.vstack(X)   # shape (n_spettri, 7054)
y = np.array(y)
nomi_validi = np.array(nomi_validi)

print("Shape X:", X.shape)  # es: (100, 7054)
print("Shape y:", y.shape)  # es: (100,)

# ==============================
# 3. Creazione modello
# ==============================
model = Pipeline([
    ("scaler", StandardScaler()),
    ("nn", NearestNeighbors(n_neighbors=10, metric="cosine"))
])

# ==============================
# 4. Addestramento
# ==============================
model.fit(X)

# ==============================
# 5. Query spettro nuovo
# ==============================
# esempio: uso il primo spettro del dataset come query
nuovo_spettro = X[6]

print(f"Molecola: {nomi_validi[6]} [ID {y[6]}]")


# nuovo_spettro è shape (7054,)
nuovo_spettro = nuovo_spettro.reshape(1, -1)

# Trasforma con scaler + PCA
X_transf = model.named_steps["scaler"].transform(nuovo_spettro)

# Trova i vicini
distances, indices = model.named_steps["nn"].kneighbors(X_transf)

# Ottieni i nomi e gli ID corrispondenti
nomi_simili = nomi_validi[indices[0]]
id_simili = y[indices[0]]

print("\nTop-10 molecole più simili:")
for rank, (nome_mol, id_mol, dist) in enumerate(zip(nomi_simili, id_simili, distances[0]), start=1):
    print(f"{rank}) Molecola: {nome_mol} [ID {id_mol}]  |  Distanza = {dist:.4f}")