from shiny import module, ui, reactive, render

import os
from pathlib import Path
here = Path(__file__).parent.parent

@module.ui
def visualizza_ui():
    return ui.nav_panel(
        "Visualizza",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "select_molecola",
                    "Seleziona la molecola da visualizzare",
                    choices = []
                ),
                ui.input_select(
                    "colore_molecola",
                    "Seleziona il colore dello spettro",
                    {
                        "red": "Rosso", 
                        "blue": "Blu", 
                        "green": "Verde",
                        "black": "Nero",
                        "yellow": "Giallo"
                    }
                ),
                ui.input_checkbox(
                    "confronto",
                    "Confronta la molecola",
                    False
                ),
                ui.panel_conditional(
                    "input.confronto",
                    ui.input_select(
                        "select_confronto",
                        "Seleziona la molecola di confronto",
                        choices = []
                    ),
                    ui.input_select(
                    "colore_standard",
                    "Seleziona il colore dello spettro",
                    {
                        "red": "Rosso", 
                        "blue": "Blu", 
                        "green": "Verde",
                        "black": "Nero",
                        "yellow": "Giallo"
                    }
                ),
                ),
                ui.input_checkbox_group(  
                    "selectize_bande",  
                    "Seleziona i gruppi da visualizzare:",
                    choices = [],  
                ),
                ui.input_action_button(
                    "visualizza_molecola",
                    "Visualizza la molecola"
                )
            ),
            ui.output_plot("spettro_selezionato_plot"),
        ),
        ui.output_image("image")
    )

@module.server
def visualizza_server(input, output, session, bande_def, spettri):
    # Crea la checkbox per vedere le bande dei gruppi funzionali
    # nella schermata di visualizzazione
    @reactive.effect
    def selectize_bande():
        bande_disponibili = bande_def.get_gruppi_funzionali(False)

        ui.update_checkbox_group(
            "selectize_bande",
            choices = {x[0]: x[1] for x in bande_disponibili}
        )

    # Aggiorna il dropdown con gli spettri disponibili
    @reactive.effect
    def _():
        spettri_disponibili = spettri.get_spettri()

        ui.update_select("select_molecola", choices=spettri_disponibili)
        ui.update_select("select_confronto", choices=spettri_disponibili)

    # Funzione per visualizzare il plot della molecola nella schermata
    # di visualizzazione
    @render.plot
    @reactive.event(input.visualizza_molecola)
    def spettro_selezionato_plot():
        # Recupera la molecola selezionata
        molecola_scelta = input.select_molecola()
        spettro_scelto = spettri.get_spettro(molecola_scelta)

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

        # Recupera la molecola di confronto, se selezionata
        spettro_confronto = spettri.get_spettro(input.select_confronto()) if input.confronto() else None

        # Recupera le bande selezionate
        bande_selezionate = input.selectize_bande()

        # Genera e restituisce il grafico
        return spettri.render_plot(
            spettro_scelto, 
            bande_selezionate, 
            spettro_confronto, 
            input.colore_molecola(), 
            input.colore_standard()
        )
    
    # Per verificare se c'è il file dell'immagine della molecola
    def file_presente(cartella, nome_file):
        return any(f.stem == nome_file for f in Path(cartella).iterdir())
