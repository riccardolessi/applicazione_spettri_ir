from shiny import App, ui, render, reactive
import jcamp
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import json
from lib import spettri

app_ui = ui.page_navbar(
    ui.nav_panel("Inserimento", 
        ui.input_file("file_upload", "Carica un file", multiple=False),
        ui.output_text("file_info"),
        ui.input_action_button("save", "Salva lo spettro"),
        ui.output_plot("spettro_plot"),
    ),
    ui.nav_panel("Visualizza",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "select_molecola",
                    "Seleziona la molecola da visualizzare",
                    choices = []
                ),
                ui.input_action_button(
                    "visualizza_molecola",
                    "Visualizza la molecola"
                )
            ),
        ui.output_plot("spettro_selezionato_plot"),
        ),
    ),
    title="App with navbar",  
    id="page"
)

def server(input, output, session):
    spettro_corrente = reactive.value(None)

    # Aggiorna il dropdown con gli spettri disponibili
    @reactive.effect
    @reactive.event(input.page)
    def _():
        spettri_disponibili = spettri.get_spettri()
        ui.update_select("select_molecola", choices=spettri_disponibili)

    # Legge il file e restituisce i dati dello spettro
    @reactive.calc
    def spettro():
        file = input.file_upload()
        if not file or len(file) == 0:
            return None  # Nessun file selezionato

        file_path = file[0]['datapath']
        nome_file = file[0]['name']

        dati_spettro = jcamp.jcamp_readfile(file_path)
        metadati = spettri.get_dati_spettro(nome_file)

        return {"dati": dati_spettro, "metadati": metadati}

    
    @render.text
    @reactive.event(input.file_upload)
    def file_info():
        grafico = spettro()
        spettro_corrente.set(spettro())
        return grafico

    # Disegna il grafico dello spettro caricato
    @render.plot
    @reactive.event(input.file_upload)
    def spettro_plot():
        dati = spettro()
        if not dati:
            return None  # Evita errori se il dato è nullo
        
        data = dati['dati']
        if 'x' not in data or 'y' not in data:
            return None  # Evita errori se il formato è sbagliato
        
        # Estrae i dati dell'asse x e y
        x = np.array(data['x'])
        y = np.array(data['y'])

        # Crea il grafico
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(x, y, label="Spettro DX", color="blue")
        ax.set_xlabel("Frequenza / Lunghezza d'onda")
        ax.set_ylabel("Intensità")
        ax.set_title("Grafico dello Spettro DX")
        ax.legend()
        ax.grid()

        ax.invert_xaxis()

        return fig

    @reactive.effect
    @reactive.event(input.save)
    def save():
        result = spettri.save_spettro(spettro_corrente())
        if not result:
            ui.notification_show(
                result,
                type="error",
                duration=4,
            )
        else:
            ui.notification_show(
                result,
                type="message",
                duration=4,
            )

    @render.plot
    @reactive.event(input.visualizza_molecola)
    def spettro_selezionato_plot():
        scelta = input.select_molecola()
        spettro_scelto = spettri.get_spettro(scelta)

        # Estrae i dati dell'asse x e y
        x = spettro_scelto["dati_spettro"]['x']
        y = spettro_scelto["dati_spettro"]['y']

        # Crea il grafico
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(x, y, label="Spettro DX", color="blue")
        ax.set_xlabel("Frequenza / Lunghezza d'onda")
        ax.set_ylabel("Intensità")
        ax.set_title(f"Spettro della molecola: {spettro_scelto['nome_molecola']}")
        ax.legend()
        ax.grid()

        ax.invert_xaxis()

        return fig

app = App(app_ui, server)

