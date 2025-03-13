from shiny import module, ui, render

@module.ui
def gruppi_funzionali_ui():
    return (
            ui.output_data_frame("bande")
        )

@module.server
# renderizza le bande presenti nel db nella sezione bande gruppi
# funzionali come df
def gruppi_funzionali_server(input, output, session, bande_def):
    @render.data_frame
    def bande():
        df = bande_def.get_gruppi_funzionali(True)

        return render.DataTable(df)
