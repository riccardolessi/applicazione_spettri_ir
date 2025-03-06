from shiny import App, ui, render, reactive
import jcamp
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import json
from lib import spettri
from lib.spettro import Spettro

app_ui = ui.page_navbar(
    ui.nav_panel("Inserimento", 
        ui.input_file("file_upload", "Carica un file", multiple=False),
        ui.input_action_button("save", "Salva lo spettro"),
        ui.output_text('info_molecola'),
        ui.output_plot("spettro_plot")
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
    # Aggiorna il dropdown con gli spettri disponibili
    @reactive.effect
    @reactive.event(input.page)
    def _():
        spettri_disponibili = spettri.get_spettri()
        ui.update_select("select_molecola", choices=spettri_disponibili)

    # Legge il file e restituisce i dati dello spettro
    @reactive.calc
    @reactive.event(input.file_upload)
    def spettro():
        file = input.file_upload()
        if not file or len(file) == 0:
            return None  # Nessun file selezionato

        file_path = file[0]['datapath']
        nome_file = file[0]['name']
        
        session.spettro_oggetto = Spettro(file_path, nome_file)
        data = session.spettro_oggetto.get_dati_spettro()
        
        return data

    @render.text
    @reactive.event(input.file_upload)
    def info_molecola():
        dati = spettro()
        return dati

    # Disegna il grafico dello spettro caricato
    @render.plot
    @reactive.event(input.file_upload)
    def spettro_plot():
        dati = spettro()
        
        fig = spettri.render_plot(dati)

        return fig

    @reactive.effect
    @reactive.event(input.save)
    def save():
        duplicato = session.spettro_oggetto.check_duplicati_db()

        if duplicato:
            ui.notification_show(
                "molecola già presente nel DB",
                type="error",
                duration=4,
                close_button=False,
            )
            ui.update_action_button(
                "save",
                disabled = True
            )
            return None

        result = spettri.save_spettro(spettro())
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

        fig = spettri.render_plot(spettro_scelto)

        return fig

app = App(app_ui, server)

