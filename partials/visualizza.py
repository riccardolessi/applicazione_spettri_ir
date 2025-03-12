from shiny import App, ui, render, reactive

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
                    )
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