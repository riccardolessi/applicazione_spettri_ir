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
        dati TEXT NOT NULL,  -- JSON con i valori x e y
        data DATE DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("Database creato con successo!")

if __name__ == "__main__":
    setup_db()
