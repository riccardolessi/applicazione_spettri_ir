from shiny import module, ui, render, reactive

@module.ui
def inserimento_ui():
    return (
        ui.input_file("file_upload", "Carica un file", multiple=False),
        ui.input_action_button("save", "Salva lo spettro"),
        ui.output_text('info_molecola'),
        ui.output_plot("spettro_plot"),
        ui.input_dark_mode(mode="dark"),
    )

@module.server
def inserimento_server(input, output, session, Spettro, spettri):
    # Legge il file e restituisce i dati dello spettro
    @reactive.calc
    @reactive.event(input.file_upload)
    def spettro():
        file = input.file_upload()
        if not file or len(file) == 0:
            return None  # Nessun file selezionato

        file_path = file[0]['datapath']
        nome_file = file[0]['name']

        session.spettro_oggetto = Spettro(file_path, nome_file)
        data = session.spettro_oggetto.get_dati_spettro()

        # Abilita il bottone anche se precedentemente disabilitato
        ui.update_action_button(
                "save",
                disabled = False
            )

        return data

    # Renderizza i dati della molecola per debug
    @render.text
    @reactive.event(input.file_upload)
    def info_molecola():
        dati = spettro()
        return dati
    
    # Disegna il grafico dello spettro caricato
    @render.plot
    @reactive.event(input.file_upload)
    def spettro_plot():
        dati = session.spettro_oggetto.get_dati_spettro()

        fig = spettri.render_plot(dati)

        return fig
    
    # Funzione per verificare se la molecola è già nel DB
    # controlla data e ora dello spettro
    @reactive.effect
    @reactive.event(input.save)
    def save():
        duplicato = session.spettro_oggetto.check_duplicati_db()

        if duplicato:
            ui.notification_show(
                "molecola già presente nel DB",
                type="error",
                duration=4,
                close_button=False,
            )
            ui.update_action_button(
                "save",
                disabled = True
            )
            return None

        result = session.spettro_oggetto.save_spettro()

        ui.notification_show(
            result['message'],
            type= result['type'],
            duration=4,
        )