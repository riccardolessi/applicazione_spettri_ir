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

        file_info = file[0]
        file_path, nome_file = file_info['datapath'], file_info['name']

        try:
            session.spettro_oggetto = Spettro(file_path, nome_file)
            data = session.spettro_oggetto.get_dati_spettro()

            # Abilita il bottone "save"
            ui.update_action_button("save", disabled=False)

            return data

        except Exception as e:
            return f"Errore nel caricamento: {e}"


    # Renderizza i dati della molecola per debug
    @render.text
    @reactive.event(input.file_upload)
    def info_molecola():
        return spettro() or "Nessun dato disponibile"
    

    # Disegna il grafico dello spettro caricato
    @render.plot
    @reactive.event(input.file_upload)
    def spettro_plot():
        spettro_oggetto = getattr(session, "spettro_oggetto", None)
        if not spettro_oggetto: # Nessuno spettro caricato
            ui.notification_show(
                "Errore: nessun spettro caricato.",
                type="error",
                duration=4,
                close_button=True,
            )
            return
        
        try:
            dati_spettro = session.spettro_oggetto.get_dati_spettro()
            if dati_spettro is None:
                return None
            return spettri.render_plot(dati_spettro)
        
        except Exception as e:
            print(f"Errore nel rendering del grafico: {e}")
            return None


    # Funzione per verificare se la molecola è già nel DB
    # controlla data e ora dello spettro
    @reactive.effect
    @reactive.event(input.save)
    def save():
        spettro_oggetto = getattr(session, "spettro_oggetto", None)
        if not spettro_oggetto: # Nessuno spettro caricato
            ui.notification_show(
                "Errore: nessun spettro caricato.",
                type="error",
                duration=4,
                close_button=True,
            )
            return
        
        try:
            esiste_gia = spettro_oggetto.check_duplicati_db()

            if esiste_gia:
                ui.notification_show(
                    "molecola già presente nel DB",
                    type="error",
                    duration=4,
                    close_button=False,
                )
                ui.update_action_button("save", disabled = True)
                return None

            risultato_salvataggio = spettro_oggetto.save_spettro()

            ui.notification_show(
                risultato_salvataggio.get("message", "Salvataggio completato."),
                type=risultato_salvataggio.get("type", "success"),
                duration=4,
            )

        except Exception as e:
            ui.notification_show(
                f"Errore durante il salvataggio: {e}",
                type="error",
                duration=4,
            )