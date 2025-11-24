from shiny import module, ui, reactive, render
import pandas as pd
from prova_ml import *
@module.ui
def similarita_ui():
    return(
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "select_molecola",
                    "Seleziona la molecola da visualizzare",
                    choices = []
                ),
                ui.input_radio_buttons(  
                    "parametro_similarita",  
                    "Seleziona un'opzione",  
                    {"1": "Seleziona il numero di molecole simili", "2": "Seleziona un threshold di similarità"},  
                ),  
                ui.panel_conditional(
                    "input.parametro_similarita == '1'",
                    ui.input_slider(
                        "num_simili",
                        "Seleziona il numero di molecole simili da trovare",
                        min = 1,
                        max = 20,
                        value = 3
                    )
                ),
                ui.panel_conditional(
                    "input.parametro_similarita == '2'",
                    ui.input_slider(
                        "threshold",
                        "Seleziona threshold di similarità",
                        min = 0,
                        max = 2,
                        step = 0.1,
                        value = 0.1
                    )
                ),
                ui.input_action_button(
                    "calcola_similarita",
                    "Calcola similarità"
                ),
            ),
            ui.output_data_frame("tabella_risultati")
        )
    )

@module.server
def similarita_server(input, output, session, spettri):
    # Variabile reattiva per contenere i risultati
    risultati_reactive = reactive.Value(None)

    @reactive.effect
    @reactive.event(input.calcola_similarita)
    def _():
        print(input.select_molecola())
        if input.parametro_similarita() == "1":
            numeri_simili = input.num_simili()
            risultati = calcola_similarita(molecola = input.select_molecola(), numero_simili= numeri_simili + 1)
        else:
            threshold = input.threshold()
            risultati = calcola_similarita(molecola = input.select_molecola(), threshold=threshold)

        df = pd.DataFrame(risultati)
        df = df.sort_values(by="distanza").reset_index(drop=True)
        df = df.drop(df.index[0]).reset_index(drop=True)
        risultati_reactive.set(df[["nome", "distanza"]])
    

    @render.data_frame
    def tabella_risultati():
        df = risultati_reactive.get()
        if df is None:
            return pd.DataFrame()
        return df


    @reactive.effect
    def _():
        spettri_disponibili = get_nomi_validi()

        ui.update_select("select_molecola", choices=spettri_disponibili)
