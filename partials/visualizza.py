from shiny import App, ui, render, reactive

def visualizza_ui():
    return ui.nav_panel("Visualizza",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "select_molecola",
                    "Seleziona la molecola da visualizzare",
                    choices = []
                ),
                ui.input_selectize(  
                    "selectize_bande",  
                    "Seleziona i gruppi da visualizzare:",
                    choices = [],
                    multiple=True,  
                ),
                ui.input_action_button(
                    "visualizza_molecola",
                    "Visualizza la molecola"
                )
            ),
        ui.output_plot("spettro_selezionato_plot"),
        ),
    )