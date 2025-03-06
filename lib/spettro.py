import jcamp
import sqlite3
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(base_dir, "spettri.db")

class Spettro:
    def __init__(self, file_path, nome_file):
        self.conn = sqlite3.connect(db_path)
        self.file_path = file_path
        self.dati_spettro = jcamp.jcamp_readfile(file_path)
        self.nome_file = nome_file
        
    def get_dati_spettro(self):
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

        self.check_duplicati_db()

        return {"dati": self.dati_spettro, "metadati": self.data}

    def save_spettro_db():
        return None

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

    # Funzione per creare il nome dell spettro
    def nome_spettro(self, namelist):
        nome = namelist[2][3:] + "/"
        nome += namelist[2][:3] + "/"
        nome += namelist[3].split('.')[0] + "/" # Splitta "ATR.dx" in "ATR"
        nome += namelist[1]

        return nome

    def check_tipo_prova(self, nome):
        if (nome[:3].lower() == "std"):
            tipologia = "STD"
        elif(nome[:3].lower() == "inc"):
            tipologia = "INC"
        else:
            tipologia = "Sconosciuta"
        
        return tipologia