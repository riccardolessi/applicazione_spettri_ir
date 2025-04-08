from shiny import module, ui, reactive, render
import pandas as pd

@module.ui
def insert_db_ui():
    return (
        ui.h2("Prova Data Frame editabile"),
        ui.input_select(
            "select",
            "Seleziona tabella",
            choices = []
        ),
        ui.output_data_frame("prova"),
        ui.output_text("show_data"), 
        ui.input_action_button("bottone_test", "Clicca qui"),
        ui.input_action_button("bottone_due", "Salva")
    )

@module.server
def insert_db_server(input, output, session, test):
    
    @reactive.effect
    def select():
        tabelle = test.tabelle()
        ui.update_select(
            "select",
            choices = tabelle
        )
    
    @reactive.effect
    @reactive.event(input.bottone_test)
    def _():
        colonne = test.colonne(input.select())
        lista_colonne = [x[1] for x in colonne]
        print(lista_colonne)
        
        df = pd.DataFrame(columns = lista_colonne)
        pippo = ['' for _ in range(len(lista_colonne))]
        print(pippo)
        df.loc[0] = pippo

        print(df)

        @render.data_frame
        def prova():
            return render.DataGrid(df, editable = True)