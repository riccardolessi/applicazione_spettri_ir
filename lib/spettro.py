import jcamp
import sqlite3
import os
import json

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

class Spettro:
    def __init__(self, file_path, nome_file):
        self.conn = sqlite3.connect(db_path)
        self.file_path = file_path
        self.dati_spettro = jcamp.jcamp_readfile(file_path)
        self.nome_file = nome_file

    # Funzione per ottenere i dati dello spettro (grafico + nome)
    def get_dati_spettro(self):
        
        self.check_nome_db(self.nome_file)

        return {"dati": self.dati_spettro, "metadati": self.data}

    # Funzione per salvare lo spettro nel DB
    def save_spettro(self):
        dati_spettro = self.get_dati_spettro()

        if not dati_spettro:
            return None

        # Serializza in JSON i dati
        try:
            dati_json = json.dumps({
                "x": dati_spettro["dati"]["x"].tolist(),
                "y": dati_spettro["dati"]["y"].tolist()
            })
        except Exception as e:
            return f"Errore nella serializzazione dei dati: {e}"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO spettri (nome, data_spettro, tipologia_spettrometro, tipologia_prova, dati) VALUES(?, ?, ?, ?, ?)",
        (dati_spettro["metadati"]["nome_molecola_db"], dati_spettro["metadati"]["data_ora"], dati_spettro["metadati"]["tipologia_spettrometro"], dati_spettro["metadati"]["tipologia_prova"], dati_json))

        conn.commit()
        conn.close()

        return "Molecola inserita nel database con successo"


    # Funzione per verificare nel DB se la molecola è già presente
    # Verifica con nome + data e ora
    def check_duplicati_db(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spettri WHERE nome = ? AND data_spettro = ?", (self.data['nome_molecola_db'], self.data['data_ora']))
        corrispondenza_db = cursor.fetchall()
        conn.close()

        if (corrispondenza_db[0][0] == 0):
            return False
        else:
            return True

    # Funzione per creare il nome dell spettro da inserire nel DB
    # CLORARIOIDRATO/STD/ATR/2024-05-22
    def nome_spettro(self, namelist):
        nome = namelist[2][3:] + "/"
        nome += namelist[2][:3] + "/"
        nome += namelist[3].split('.')[0] + "/" # Splitta "ATR.dx" in "ATR"
        nome += namelist[1]

        return nome

    # Funzione per distinguere le prove standard da incognite
    def check_tipo_prova(self, nome):
        if (nome[:3].lower() == "std"):
            tipologia = "STD"
        elif(nome[:3].lower() == "inc"):
            tipologia = "INC"
        else:
            tipologia = "Sconosciuta"

        return tipologia
    
    # Funzione per verificare e creare le info della molecola
    # Implementare i controlli per evitare problemi nell'inserimento nel db
    def check_nome_db(self, name):
        namelist = self.nome_file.split("_")
        name = namelist[2]
        data = self.dati_spettro['date'] + " " + self.dati_spettro['time']

        tipologia = self.check_tipo_prova(name)

        nome_molecola_db = self.nome_spettro(namelist)

        self.data = {
            'data': namelist[1],
            'data_ora': data,
            'molecola': name[3:],
            'nome_molecola_db': nome_molecola_db,
            'tipologia_prova': tipologia,
            'tipologia_spettrometro': namelist[3].split('.')[0], # Splitta "ATR.dx" in "ATR"
        }