import os
import sqlite3

# Path del DB, risolto rispetto alla posizione di questo file come negli
# altri moduli del progetto: cosi' lo script funziona da qualsiasi cwd
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "spettri.db")


def setup_db(percorso_db=db_path):
    """
    Crea lo schema del database se non esiste gia'.

    Le CREATE TABLE riproducono lo schema di spettri.db, ordine delle colonne
    compreso. L'ordine fa parte del contratto: piu' punti del codice leggono
    le righe per indice numerico (banda[2] e banda[3] sono min e max in
    lib/spettri.py, banda[6] e' lo SMARTS in modules/analisi_molecola.py),
    quindi non va cambiato senza aggiornare anche quei moduli.

    La funzione e' idempotente: usa IF NOT EXISTS e non tocca i dati presenti.
    """
    conn = sqlite3.connect(percorso_db)
    cursor = conn.cursor()

    # Anagrafica delle fonti bibliografiche di spettri e bande.
    # Creata per prima perche' le altre tabelle la referenziano.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fonti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    )
    """)

    # Gruppi funzionali a cui appartengono le bande di assorbimento
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gruppi_funzionali (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gruppo_funzionale TEXT NOT NULL,
        smile_gruppo TEXT
    )
    """)

    # Tabella per gli spettri
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spettri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_spettro DATE,
        tipologia_spettrometro TEXT,
        tipologia_prova TEXT,
        fonte_spettri INT,
        dati TEXT NOT NULL,  -- JSON con i valori x e y
        data DATE DEFAULT CURRENT_TIMESTAMP,
        smiles TEXT,
        FOREIGN KEY (fonte_spettri) REFERENCES fonti(id)
    )
    """)

    # Bande di assorbimento: intervallo min-max in cm-1 e pattern SMARTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bande_gruppi_funzionali (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gruppo_funzionale TEXT NOT NULL,
        min INTEGER NOT NULL,
        max INTEGER NOT NULL,
        id_gruppo INT,
        fonte_bande INT,
        smarts TEXT,
        FOREIGN KEY (id_gruppo) REFERENCES gruppi_funzionali(id),
        FOREIGN KEY (fonte_bande) REFERENCES fonti(id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"Database creato con successo: {percorso_db}")


if __name__ == "__main__":
    setup_db()
