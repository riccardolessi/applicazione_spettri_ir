from shiny import App, ui, render, reactive
from lib import spettri
from lib.spettro import Spettro
from lib import bande_gruppi_funzionali as bande_def
from partials import inserimento, visualizza

import os
from pathlib import Path
here = Path(__file__).parent

app_ui = ui.page_navbar(
    inserimento.inserimento_ui(),

    visualizza.visualizza_ui(),

    ui.nav_panel("Bande gruppi funzionali",
        ui.output_data_frame("bande"),
    ),

    title="App with navbar",  
    id="page"
)

def server(input, output, session):
    # Crea la checkbox per vedere le bande dei gruppi funzionali
    # nella schermata di visualizzazione
    @reactive.effect
    def selectize_bande():
        bande_disponibili = bande_def.get_gruppi_funzionali(False)

        ui.update_checkbox_group(
            "selectize_bande",
            choices = {x[0]: x[1] for x in bande_disponibili}
        )
        
    # renderizza le bande presenti nel db nella sezione bande gruppi
    # funzionali come df
    @render.data_frame
    def bande():
        df = bande_def.get_gruppi_funzionali(True)

        return render.DataTable(df, editable = True)

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

    # Renderizza i dati della molecola per debug
    @render.text
    @reactive.event(input.file_upload)
    def info_molecola():
        dati = spettro()
        return dati

    # Disegna il grafico dello spettro caricato
    @render.plot
    @reactive.event(input.file_upload)
    def spettro_plot():
        dati = session.spettro_oggetto.get_dati_spettro()
        
        fig = spettri.render_plot(dati)

        return fig

    # Funzione per verificare se la molecola è già nel DB
    # controlla data e ora dello spettro
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
        
        result = session.spettro_oggetto.save_spettro()

        if result.status == "error":
            ui.notification_show(
                result.message,
                type="error",
                duration=4,
            )
        else:
            ui.notification_show(
                result.message,
                type="message",
                duration=4,
            )

    # Funzione per visualizzare il plot della molecola nella schermata
    # di visualizzazione
    @render.plot
    @reactive.event(input.visualizza_molecola)
    def spettro_selezionato_plot():
        scelta = input.select_molecola()
        spettro_scelto = spettri.get_spettro(scelta)

        cartella = here / "images"
        nome_molecola = spettro_scelto['metadati']['molecola'].split("/")[0]

        file = file_presente(cartella, nome_molecola)
        if file:
            @render.image
            def image():
                img = {"src": here / f"images/{nome_molecola}.png"}
                return img
        else:
            @render.image
            def image():
                return None
        
        bande_selezionate = input.selectize_bande()

        fig = spettri.render_plot(spettro_scelto, bande_selezionate)

        return fig
    
    # Per verificare se c'è il file dell'immagine della molecola
    def file_presente(cartella, nome_file):
        return any(f.stem == nome_file for f in Path(cartella).iterdir())
  

app = App(app_ui, server)