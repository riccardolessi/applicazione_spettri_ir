from shiny import module, ui, reactive, render

import os
from pathlib import Path
here = Path(__file__).parent.parent

@module.ui
def singola_molecola_ui():
    return (
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "select_molecola",
                    "Seleziona la molecola da visualizzare",
                    choices = []
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
        ui.layout_columns(
            ui.output_image("image"),
            ui.output_text("fonte_spettri")
        )
    )

@module.server
def singola_molecola_server(input, output, session, bande_def, spettri):
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
        if not spettro_molecola['fonte_spettro']:
            spettro_molecola['fonte_spettro'] = "Non specificata"
            
        @render.text
        def fonte_spettri():
            return f"Fonte dello spettro: {spettro_molecola['fonte_spettro']}"

        # Recupera le bande selezionate
        bande_selezionate = input.selectize_bande()
        
        # Controlla se esiste un'immagine associata alla molecola e la renderizza
        @render.image
        def image():
            img = render_molecola_image(spettro_molecola)
            return img

        # Recupera le bande selezionate
        bande_selezionate = input.selectize_bande()

        # Genera e restituisce il grafico
        return spettri.render_plot(
            spettro_molecola, 
            bande_selezionate, 
            None,
            "red", 
            None
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

