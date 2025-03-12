import sqlite3

def setup_db():
    conn = sqlite3.connect("spettri.db")
    cursor = conn.cursor()

    # Tabella per gli spettri
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spettri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_spettro DATE,
        tipologia_spettrometro TEXT,
        tipologia_prova TEXT,
        fonte_spettri int,
        dati TEXT NOT NULL,  -- JSON con i valori x e y
        data DATE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (fonte_spettri) REFERENCES fonti(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bande_gruppi_funzionali (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gruppo_funzionale TEXT NOT NULL,
        min INTEGER NOT NULL,
        max INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fonti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Database creato con successo!")

if __name__ == "__main__":
    setup_db()
