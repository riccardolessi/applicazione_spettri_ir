from shiny import module, ui, reactive, render
from pathlib import Path

here = Path(__file__).parent.parent

COLORI = {
    "red": "Rosso",
    "blue": "Blu",
    "green": "Verde",
    "black": "Nero",
    "yellow": "Giallo",
}

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@module.ui
def visualizza_ui():
    return ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("select_molecola", "Seleziona la molecola da visualizzare", choices=[]),
            ui.input_select("colore_molecola", "Seleziona il colore dello spettro", COLORI),
            ui.input_checkbox("confronto", "Confronta la molecola", False),
            ui.panel_conditional(
                "input.confronto",
                ui.input_select("select_confronto", "Seleziona la molecola di confronto", choices=[]),
                ui.input_select("colore_standard", "Seleziona il colore dello spettro di confronto", COLORI),
            ),
            ui.input_checkbox("visualizza_bande", "Visualizza le bande"),
            ui.panel_conditional(
                "input.visualizza_bande",
                ui.input_checkbox_group("selectize_bande", "Seleziona i gruppi da visualizzare:", choices=[]),
            ),
            ui.input_action_button("visualizza_molecola", "Visualizza la molecola"),
        ),
        ui.output_plot("spettro_selezionato_plot"),
    )


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

@module.server
def visualizza_server(input, output, session, bande_def, spettri):

    # -- Stato reattivo condiviso -----------------------------------------

    _spettro_corrente: reactive.Value[dict | None] = reactive.value(None)
    _confronto_corrente: reactive.Value[dict | None] = reactive.value(None)

    # -- Sync select / checkbox -------------------------------------------

    @reactive.effect
    def _sync_spettri():
        disponibili = spettri.get_spettri()
        ui.update_select("select_molecola", choices=disponibili)
        ui.update_select("select_confronto", choices=disponibili)

    @reactive.effect
    def _sync_gruppi():
        gruppi = bande_def.get_gruppi_funzionali(False)
        ui.update_checkbox_group("selectize_bande", choices={x[0]: x[1] for x in gruppi})

    # -- Aggiornamento stato al click -------------------------------------

    @reactive.effect
    @reactive.event(input.visualizza_molecola)
    def _aggiorna_spettri():
        id_molecola = input.select_molecola()
        _spettro_corrente.set(spettri.get_spettro(id_molecola) if id_molecola else None)
        _confronto_corrente.set(spettri.get_spettro(input.select_confronto()) if input.confronto() else None)

    # -- Render -----------------------------------------------------------

    @render.plot
    def spettro_selezionato_plot():
        spettro = _spettro_corrente()
        if spettro is None:
            return None

        return spettri.render_plot(
            spettro,
            input.selectize_bande(),
            _confronto_corrente(),
            input.colore_molecola(),
            input.colore_standard(),
        )




# from shiny import module, ui, reactive, render

# import os
# from pathlib import Path
# here = Path(__file__).parent.parent

# @module.ui
# def visualizza_ui():
#     return (ui.layout_sidebar(
#             ui.sidebar(
#                 ui.input_select(
#                     "select_molecola",
#                     "Seleziona la molecola da visualizzare",
#                     choices = []
#                 ),
#                 ui.input_select(
#                     "colore_molecola",
#                     "Seleziona il colore dello spettro",
#                     {
#                         "red": "Rosso", 
#                         "blue": "Blu", 
#                         "green": "Verde",
#                         "black": "Nero",
#                         "yellow": "Giallo"
#                     }
#                 ),
#                 ui.input_checkbox(
#                     "confronto",
#                     "Confronta la molecola",
#                     False
#                 ),
#                 ui.panel_conditional(
#                     "input.confronto",
#                     ui.input_select(
#                         "select_confronto",
#                         "Seleziona la molecola di confronto",
#                         choices = []
#                     ),
#                     ui.input_select(
#                     "colore_standard",
#                     "Seleziona il colore dello spettro",
#                     {
#                         "red": "Rosso", 
#                         "blue": "Blu", 
#                         "green": "Verde",
#                         "black": "Nero",
#                         "yellow": "Giallo"
#                     }
#                 ),
#                 ),
#                 ui.input_checkbox(
#                     "visualizza_bande",
#                     "Visualizza le bande"
#                 ),
#                 ui.panel_conditional(
#                     "input.visualizza_bande",
#                     ui.input_checkbox_group(  
#                         "selectize_bande",  
#                         "Seleziona i gruppi da visualizzare:",
#                         choices = [],  
#                     ),
#                     # ui.input_checkbox_group(  
#                     #     "selectize_bande_new",  
#                     #     "Seleziona le bande da visualizzare:",
#                     #     choices = [],  
#                     # ),
#                     # ui.input_slider(
#                     #     "slider_bande",
#                     #     "Seleziona la larghezza delle bande singole",
#                     #     0, 50, 10
#                     # ),
#                 ),
#                 ui.input_action_button(
#                     "visualizza_molecola",
#                     "Visualizza la molecola"
#                 )
#             ),
#             ui.output_plot("spettro_selezionato_plot"),
#         )
#     )

# @module.server
# def visualizza_server(input, output, session, bande_def, spettri):
#     # Crea la checkbox per vedere le bande dei gruppi funzionali
#     # nella schermata di visualizzazione
#     @reactive.effect
#     def selectize_bande():
#         gruppi_funzionali = bande_def.get_gruppi_funzionali(False)

#         # Converte da tuple a dizionario
#         opzioni_bande = {x[0]: x[1] for x in gruppi_funzionali}

#         ui.update_checkbox_group("selectize_bande", choices=opzioni_bande)


#     # Aggiorna il dropdown con gli spettri disponibili
#     @reactive.effect
#     def _():
#         spettri_disponibili = spettri.get_spettri()

#         ui.update_select("select_molecola", choices=spettri_disponibili)
#         ui.update_select("select_confronto", choices=spettri_disponibili)


#     # Funzione per visualizzare il plot della molecola nella schermata
#     # di visualizzazione
#     @render.plot
#     @reactive.event(input.visualizza_molecola)
#     def spettro_selezionato_plot():
        
#         id_molecola = input.select_molecola()
#         if not id_molecola:
#             return None # Nessuna molecola selezionata

#         # Recupera lo spettro della molecola selezionata
#         spettro_molecola = spettri.get_spettro(id_molecola)

#         # Recupera lo spettro di confronto se selezionato
#         spettro_confronto = spettri.get_spettro(input.select_confronto()) if input.confronto() else None

#         # Recupera le bande selezionate
#         bande_selezionate = input.selectize_bande()

#         # Recupera la molecola di confronto, se selezionata
#         spettro_confronto = spettri.get_spettro(input.select_confronto()) if input.confronto() else None

#         # Recupera le bande selezionate
#         bande_selezionate = input.selectize_bande()

#         # Genera e restituisce il grafico
#         return spettri.render_plot(
#             spettro_molecola, 
#             bande_selezionate, 
#             spettro_confronto, 
#             input.colore_molecola(), 
#             input.colore_standard()
#         )
    
#     # Per verificare se c'è il file dell'immagine della molecola
#     def file_presente(cartella, nome_file):
#         return any(f.stem == nome_file for f in Path(cartella).iterdir())
