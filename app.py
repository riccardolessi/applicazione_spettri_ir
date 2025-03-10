from shiny import App, ui, render, reactive
from lib import spettri
from lib.spettro import Spettro
from lib import bande_gruppi_funzionali as bande_def
from shinywidgets import output_widget
from partials import inserimento, visualizza
from module import counter_ui, counter_server
from modules.inserimento_spettro import inserimento_ui

app_ui = ui.page_navbar(
    inserimento.inserimento_ui(),
    visualizza.visualizza_ui(),

    ui.nav_panel("Bande gruppi funzionali",
        ui.output_data_frame("bande"),
        counter_ui("counter1", "Counter 1"),
    ),

    ui.nav_panel("Bande Gruppi Funzionali Tabella",
        ui.h2("Tabella modificabile (solo sessione)"),
        ui.output_data_frame("table")
    ),
    title="App with navbar",  
    id="page"
)

def server(input, output, session):
    @reactive.effect
    def selectize_bande():
        bande_disponibili = bande_def.get_gruppi_funzionali(False)
        ui.update_selectize(
            "selectize_bande",
            choices={x[0]: x[1] for x in bande_disponibili}
        )
        
    @render.data_frame
    def bande():
        df = bande_def.get_gruppi_funzionali(True)

        return render.DataTable(df)

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

        result = session.spettro_oggetto.save_spettro()
        
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

        bande_selezionate = input.selectize_bande()

        fig = spettri.render_plot(spettro_scelto, bande_selezionate)

        return fig

    # Mostrare la tabella modificabile
    @render.data_frame
    def table():
        return render.DataTable(bande_def.get_gruppi_funzionali(True))

    counter_server("counter1", starting_value=5)

app = App(app_ui, server)