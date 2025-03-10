from shiny import App, ui, render, reactive

def inserimento_ui():
    return ui.nav_panel("Inserimento", 
        ui.input_file("file_upload", "Carica un file", multiple=False),
        ui.input_action_button("save", "Salva lo spettro"),
        ui.output_text('info_molecola'),
        ui.output_plot("spettro_plot"),
        ui.input_dark_mode(mode="dark"),
    )