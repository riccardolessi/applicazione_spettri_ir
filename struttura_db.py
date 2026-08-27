import sqlite3

def analizza_db(nome_db):
    try:
        # Connessione al database
        conn = sqlite3.connect(nome_db)
        cursor = conn.cursor()

        # 1. Recupera i nomi di tutte le tabelle (escludendo quelle di sistema)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelle = cursor.fetchall()

        if not tabelle:
            print("Il database è vuoto o non contiene tabelle.")
            return

        print(f"--- Struttura del Database: {nome_db} ---")

        for tabella in tabelle:
            nome_tabella = tabella[0]
            print(f"\nTabella: {nome_tabella}")
            print("-" * (8 + len(nome_tabella)))

            # 2. Recupera le informazioni sulle colonne per ogni tabella
            # PRAGMA table_info restituisce: (id, nome, tipo, notnull, pk, ...)
            cursor.execute(f"PRAGMA table_info('{nome_tabella}');")
            colonne = cursor.fetchall()

            for col in colonne:
                nome_col = col[1]
                tipo_col = col[2]
                pk = " [PRIMARY KEY]" if col[5] else ""
                print(f"  - {nome_col} ({tipo_col}){pk}")

    except sqlite3.Error as e:
        print(f"Errore durante l'accesso al database: {e}")
    
    finally:
        if conn:
            conn.close()

# Inserisci qui il percorso del tuo file .db
analizza_db('spettri.db')