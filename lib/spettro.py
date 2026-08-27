import jcamp
import sqlite3
import os
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Costanti di modulo
# ---------------------------------------------------------------------------

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "spettri.db"))

_TIPO_PROVA_MAP: dict[str, str] = {
    "std": "STD",
    "inc": "INC",
}


# ---------------------------------------------------------------------------
# Eccezioni di dominio
# ---------------------------------------------------------------------------

class SpettroError(Exception):
    """Errore base per problemi legati allo spettro."""

class SpettroParsingError(SpettroError):
    """Il nome file o il contenuto JCAMP non rispetta il formato atteso."""

class SpettroDBError(SpettroError):
    """Errore durante un'operazione sul database."""


# ---------------------------------------------------------------------------
# Metadati: calcolati una volta sola, immutabili
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MetadatiSpettro:
    """
    Contenitore immutabile dei metadati estratti dal nome file e dall'header JCAMP.
    Costruito nel __init__ di Spettro: esiste sempre, non dipende
    dall'ordine di chiamata dei metodi.
    """
    molecola: str                # es. "METILPIDROSSIBENZOATO"
    nome_db: str                 # es. "METILPIDROSSIBENZOATO/STD/ATR/2022-03-30"
    data_file: str               # data estratta dal nome file (YYYY-MM-DD)
    data_ora_jcamp: str          # timestamp dall'header JCAMP ("2022-03-30 10:45:00")
    tipologia_prova: str         # "STD" | "INC" | "Sconosciuta"
    tipologia_spettrometro: str  # es. "ATR", "NUJOL"


# ---------------------------------------------------------------------------
# Classe principale
# ---------------------------------------------------------------------------

class Spettro:
    """
    Rappresenta un singolo spettro IR.

    Responsabilità:
      - Parsing del file JCAMP
      - Estrazione e validazione dei metadati dal nome file
      - Persistenza su SQLite

    Formato nome file atteso:
        TIPO_DATA_TIPOPROVAMOLECOLA_SUPPORTO.dx
        es. IR_2022-03-30_STDMETILPIDROSSIBENZOATO_ATR.dx
    """

    def __init__(self, file_path: str, nome_file: str) -> None:
        self.file_path = file_path
        self.nome_file = nome_file

        # Parsing JCAMP — fallisce subito se il file è corrotto
        try:
            self._dati_jcamp: dict[str, Any] = jcamp.jcamp_readfile(file_path)
        except Exception as e:
            raise SpettroParsingError(
                f"Impossibile leggere il file JCAMP '{nome_file}': {e}"
            ) from e

        # Metadati calcolati una volta sola nel costruttore.
        # Qualsiasi metodo può leggerli senza preoccuparsi dell'ordine
        # di chiamata o di effetti collaterali.
        self._metadati: MetadatiSpettro = self._parse_metadati()

    # ------------------------------------------------------------------
    # Proprietà pubbliche (read-only)
    # ------------------------------------------------------------------

    @property
    def metadati(self) -> MetadatiSpettro:
        return self._metadati

    @property
    def dati_jcamp(self) -> dict[str, Any]:
        return self._dati_jcamp

    def return_nome_file(self) -> str:
        return self.nome_file

    def get_dati_spettro(self) -> dict[str, Any]:
        """
        Restituisce dati grezzi e metadati nel formato atteso dall'UI.
        Tutte le chiavi presenti nell'originale self.data sono mantenute
        per compatibilità con render_plot e il layer Shiny.
        """
        return {
            "dati": self._dati_jcamp,
            "metadati": {
                "molecola":               self._metadati.molecola,
                "nome_molecola_db":       self._metadati.nome_db,
                "data":                   self._metadati.data_file,
                "data_ora":               self._metadati.data_ora_jcamp,
                "tipologia_prova":        self._metadati.tipologia_prova,
                "tipologia_spettrometro": self._metadati.tipologia_spettrometro,
            },
        }

    # ------------------------------------------------------------------
    # Operazioni DB
    # ------------------------------------------------------------------

    def check_duplicati_db(self) -> bool:
        """
        Restituisce True se esiste già uno spettro con lo stesso nome
        e timestamp nel database.
        """
        query = "SELECT COUNT(*) FROM spettri WHERE nome = ? AND data_spettro = ?"
        params = (self._metadati.nome_db, self._metadati.data_ora_jcamp)

        try:
            with sqlite3.connect(DB_PATH) as conn:
                # .execute() restituisce un cursor: fetchone() è disponibile
                count = conn.execute(query, params).fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            raise SpettroDBError(
                f"Errore durante il controllo duplicati: {e}"
            ) from e

    def save_spettro(self, fonte_spettro: int = 1) -> dict[str, str]:
        """
        Inserisce lo spettro nel database.
        Restituisce {message, type} compatibile con ui.notification_show di Shiny.
        Solleva SpettroDBError in caso di problemi, lasciando la gestione
        al layer UI.
        """
        dati_serializzati = self._serializza_dati()
        meta = self._metadati

        query = """
            INSERT INTO spettri
                (nome, data_spettro, tipologia_spettrometro, tipologia_prova, dati, fonte_spettri)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            meta.nome_db,
            meta.data_ora_jcamp,
            meta.tipologia_spettrometro,
            meta.tipologia_prova,
            dati_serializzati,
            fonte_spettro,
        )

        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(query, params)
                # commit automatico all'uscita del context manager
        except sqlite3.IntegrityError as e:
            # Vincolo UNIQUE violato: duplicato sfuggito al check preventivo
            raise SpettroDBError(
                f"Spettro già presente nel database: {e}"
            ) from e
        except sqlite3.Error as e:
            raise SpettroDBError(
                f"Errore durante il salvataggio: {e}"
            ) from e

        return {
            "message": "Molecola inserita nel database con successo",
            "type":    "message",
        }

    # ------------------------------------------------------------------
    # Metodi privati
    # ------------------------------------------------------------------

    def _parse_metadati(self) -> MetadatiSpettro:
        """
        Estrae e valida i metadati dal nome file e dall'header JCAMP.
        Chiamato una sola volta nel __init__.

        Formato atteso: TIPO_DATA_TIPOPROVAMOLECOLA_SUPPORTO.dx
        """
        parts = self.nome_file.split("_")
        if len(parts) < 4:
            raise SpettroParsingError(
                f"Nome file non valido — attesi almeno 4 segmenti separati da '_', "
                f"trovati {len(parts)}: '{self.nome_file}'"
            )

        # Segmento [1] → data file (YYYY-MM-DD)
        data_file = _valida_data(parts[1])

        # Segmento [2] → prime 3 lettere = tipo prova, resto = molecola
        prefisso_prova = parts[2][:3].lower()
        molecola       = parts[2][3:].upper()
        tipologia_prova = _TIPO_PROVA_MAP.get(prefisso_prova, "Sconosciuta")

        # Segmento [3] → supporto senza estensione
        tipologia_spettrometro = parts[3].split(".")[0].upper()

        # Timestamp dall'header JCAMP
        data_ora_jcamp = self._estrai_timestamp_jcamp()

        # Chiave composita per il DB
        nome_db = f"{molecola}/{tipologia_prova}/{tipologia_spettrometro}/{data_file}"

        return MetadatiSpettro(
            molecola=molecola,
            nome_db=nome_db,
            data_file=data_file,
            data_ora_jcamp=data_ora_jcamp,
            tipologia_prova=tipologia_prova,
            tipologia_spettrometro=tipologia_spettrometro,
        )

    def _estrai_timestamp_jcamp(self) -> str:
        """
        Combina 'date' e 'time' dall'header JCAMP.
        Restituisce stringa vuota se i campi mancano, evitando KeyError silenziosi.
        """
        data = self._dati_jcamp.get("date", "")
        ora  = self._dati_jcamp.get("time", "")
        return f"{data} {ora}".strip()

    def _serializza_dati(self) -> str:
        """
        Serializza i vettori x/y in JSON per la persistenza su DB.
        Solleva SpettroParsingError se i dati JCAMP sono malformati.
        """
        try:
            return json.dumps({
                "x": self._dati_jcamp["x"].tolist(),
                "y": self._dati_jcamp["y"].tolist(),
            })
        except KeyError as e:
            raise SpettroParsingError(
                f"Campo mancante nei dati JCAMP: {e}"
            ) from e
        except Exception as e:
            raise SpettroParsingError(
                f"Errore nella serializzazione dei dati: {e}"
            ) from e


# ---------------------------------------------------------------------------
# Utility di modulo (non legate allo stato di un'istanza)
# ---------------------------------------------------------------------------

def _valida_data(date_string: str) -> str:
    """
    Verifica che la stringa rispetti il formato YYYY-MM-DD.
    Solleva SpettroParsingError se il formato non è valido — nessun
    fallback silenzioso, perché una data errata è un dato corrotto.
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string
    except ValueError:
        raise SpettroParsingError(
            f"Data non valida nel nome file (atteso YYYY-MM-DD): '{date_string}'"
        )




# import jcamp
# import sqlite3
# import os
# import json

# # Path del DB
# base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# db_path = os.path.join(base_dir, "spettri.db")

# class Spettro:
#     def __init__(self, file_path, nome_file):
#         self.db_path = db_path
#         self.file_path = file_path
#         self.dati_spettro = jcamp.jcamp_readfile(file_path)
#         self.nome_file = nome_file

#     # Funzione per restituire il nome del file
#     def return_nome_file(self):
#         name = self.nome_file
#         return name

#     # Funzione per ottenere i dati dello spettro (grafico + nome)
#     def get_dati_spettro(self):
        
#         self.check_nome_db()

#         return {"dati": self.dati_spettro, "metadati": self.data}

#     # Funzione per salvare lo spettro nel DB
#     def save_spettro(self, fonte_spettro = 1):
#         dati_spettro = self.get_dati_spettro()

#         if not dati_spettro:
#             return {
#                 "message": "C'è un problema con il caricamento dei dati",
#                 "type": "error"
#             }

#         # Serializza in JSON i dati
#         try:
#             dati_json = json.dumps({
#                 "x": dati_spettro["dati"]["x"].tolist(),
#                 "y": dati_spettro["dati"]["y"].tolist()
#             })
#         except Exception as e:
#             return {
#                 "message": f"Errore nella serializzazione dei dati: {e}",
#                 "type": "error"
#                 }

#         with sqlite3.connect(self.db_path) as conn:
#             conn.execute(
#                 """
#                 INSERT INTO spettri
#                     (nome, data_spettro, tipologia_spettrometro, tipologia_prova, dati, fonte_spettri)
#                 VALUES (?, ?, ?, ?, ?, ?)
#                 """,
#                 (
#                     dati_spettro["metadati"]["nome_molecola_db"],
#                     dati_spettro["metadati"]["data_ora"],
#                     dati_spettro["metadati"]["tipologia_spettrometro"],
#                     dati_spettro["metadati"]["tipologia_prova"],
#                     dati_json,
#                     fonte_spettro,
#                 ),
#             )

#         return {
#             "message": "Molecola inserita nel database con successo",
#             "type": "message"
#         }


#     # Funzione per verificare nel DB se la molecola è già presente
#     # Verifica con nome + data e ora
#     def check_duplicati_db(self):
#         self.check_nome_db()
        
#         with sqlite3.connect(self.db_path) as conn:
#             conn.execute("SELECT COUNT(*) FROM spettri WHERE nome = ? AND data_spettro = ?", (self.data['nome_molecola_db'], self.data['data_ora']))
#             corrispondenza_db = conn.fetchall()

#         if (corrispondenza_db[0][0] == 0):
#             return False
#         else:
#             return True

#     # Funzione per creare il nome dell spettro da inserire nel DB
#     # CLORARIOIDRATO/STD/ATR/2024-05-22
#     def nome_spettro(self, namelist):
#         nome = namelist[2][3:] + "/"
#         nome += namelist[2][:3] + "/"
#         nome += namelist[3].split('.')[0] + "/" # Splitta "ATR.dx" in "ATR"
#         nome += namelist[1]

#         return nome

#     # Funzione per distinguere le prove standard da incognite
#     def check_tipo_prova(self, nome):
#         if (nome[:3].lower() == "std"):
#             tipologia = "STD"
#         elif(nome[:3].lower() == "inc"):
#             tipologia = "INC"
#         else:
#             tipologia = "Sconosciuta"

#         return tipologia
    
#     # Funzione per verificare e creare le info della molecola
#     # Implementare i controlli per evitare problemi nell'inserimento nel db
#     def check_nome_db(self):
#         namelist = self.nome_file.split("_")
#         name = namelist[2]
#         data = self.dati_spettro['date'] + " " + self.dati_spettro['time']

#         tipologia = self.check_tipo_prova(name)

#         nome_molecola_db = self.nome_spettro(namelist)

#         self.data = {
#             'data': namelist[1],
#             'data_ora': data,
#             'molecola': name[3:],
#             'nome_molecola_db': nome_molecola_db,
#             'tipologia_prova': tipologia,
#             'tipologia_spettrometro': namelist[3].split('.')[0], # Splitta "ATR.dx" in "ATR"
#         }
