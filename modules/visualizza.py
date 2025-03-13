from shiny import module, ui, reactive, render

import os
from pathlib import Path
here = Path(__file__).parent.parent

@module.ui
def visualizza_ui():
    return (ui.layout_sidebar(
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
        ui.output_image("image"),
    )

@module.server
def visualizza_server(input, output, session, bande_def, spettri):
    # Crea la checkbox per vedere le bande dei gruppi funzionali
    # nella schermata di visualizzazione
    @reactive.effect
    def selectize_bande():
        gruppi_funzionali = bande_def.get_gruppi_funzionali(False)

        # Converte da tuple a dizionario
        opzioni_bande = {x[0]: x[1] for x in gruppi_funzionali}

        ui.update_checkbox_group("selectize_bande", choices=opzioni_bande)


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
        
        id_molecola = input.select_molecola()
        if not id_molecola:
            return None # Nessuna molecola selezionata

        # Recupera lo spettro della molecola selezionata
        spettro_molecola = spettri.get_spettro(id_molecola)

        # Recupera lo spettro di confronto se selezionato
        spettro_confronto = spettri.get_spettro(input.select_confronto()) if input.confronto() else None

        # Recupera le bande selezionate
        bande_selezionate = input.selectize_bande()
        
        # Controlla se esiste un'immagine associata alla molecola e la renderizza
        @render.image
        def image():
            img = render_molecola_image(spettro_molecola)
            return img

        # Recupera la molecola di confronto, se selezionata
        spettro_confronto = spettri.get_spettro(input.select_confronto()) if input.confronto() else None

        # Recupera le bande selezionate
        bande_selezionate = input.selectize_bande()

        # Genera e restituisce il grafico
        return spettri.render_plot(
            spettro_molecola, 
            bande_selezionate, 
            spettro_confronto, 
            input.colore_molecola(), 
            input.colore_standard()
        )
    
    # Per verificare se c'è il file dell'immagine della molecola
    def file_presente(cartella, nome_file):
        return any(f.stem == nome_file for f in Path(cartella).iterdir())

    def render_molecola_image(spettro):
        """Verifica la presenza di un'immagine associata alla molecola e la visualizza."""
        
        cartella_immagini = here / "images"
        nome_molecola = spettro['metadati']['molecola'].split("/")[0]
        file_immagine = file_presente(cartella_immagini, nome_molecola)

        if file_immagine:
            return {"src": here / f"images/{nome_molecola}.png"}
        
        return None

    # Evita che l'immagine rimanga in attesa in caricamento
    @render.image
    def image():
        return None