from shiny import module, ui, render, reactive
from datetime import datetime, date
import pandas as pd
import random


@module.ui
def inserimento_multiplo_ui():
    return(
        ui.input_file(
            "import_files",
            "Import massivo",
            multiple = True
        ),
        ui.input_action_button(
            "import_button",
            "Importa gli spettri"
        ),
        ui.output_data_frame("spettri_da_caricare")
    )


@module.server
def inserimento_multiplo_server(input, output, session, Spettro, spettri, fonti):
    molecole_da_caricare = reactive.value()

    # Funzione per visualizzare il df con le molecole da importare
    @render.data_frame
    @reactive.event(input.import_files)
    def spettri_da_caricare():
        molecole = input.import_files()

        output = []
        datapath_output = []

        for mol in molecole:
            output.append(mol['name'])
            datapath_output.append(mol['datapath'])

        data = {
            "Molecole da caricare": output,
            "datapath": datapath_output
        }

        df = pd.DataFrame(data)
        df['Caricato nel db'] = "No"

        molecole_da_caricare.set(df)
        
        return molecole_da_caricare()


    # Funzione per importare le molecole nel db ed aggiornare il df
    @reactive.effect
    @reactive.event(input.import_button)
    def _():
        temp = molecole_da_caricare()
        
        for index, row in temp.iterrows():
            mol = row['Molecole da caricare']
            datapath = row['datapath']

            result = carica_molecola_db(mol, datapath)

            temp.at[index, 'Caricato nel db'] = result

            
        
        @render.data_frame
        def spettri_da_caricare():
            return molecole_da_caricare()
        

        return None
    

    # Logica per caricare molecola nel DB
    def carica_molecola_db(nome_molecola, datapath):

        try:
            spettro_oggetto = Spettro(datapath, nome_molecola)

            esiste_gia = spettro_oggetto.check_duplicati_db()

            if esiste_gia:
                return "Molecola già presente nel DB"
            
            risultato_salvataggio = spettro_oggetto.save_spettro()

            return risultato_salvataggio.get("message", "Salvataggio completato.")
            

        except Exception as e:
            return f"Errore nel caricamento: {e}"