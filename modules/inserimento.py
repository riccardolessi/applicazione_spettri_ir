from shiny import module, ui, render, reactive
from datetime import datetime

# IR_2022-03-30_STDMETILPIDROSSIBENZOATO_ATR.dx

@module.ui
def inserimento_ui():
    return (
        ui.input_file("file_upload", "Carica un file", multiple=False),
        # ui.panel_conditional(
        #     "input.file_upload",
        #     ui.card(
        #         ui.input_text(
        #             "nome_molecola",
        #             "Inserisci il nome della molecola"
        #         ),
        #         ui.input_date(
        #             "data_creazione_spettro",
        #             "Inserisci la data di creazione dello spettro"
        #         ),
        #         ui.input_select(
        #             "tipo_supporto",
        #             "Seleziona il supporto utilizzato",
        #             choices = ["ATR", "Nujol"]
        #         ),
        #         ui.input_select(
        #             "fonte",
        #             "Seleziona la fonte dello spettro",
        #             choices = []
        #         ),
        #     ),
        # ),
        ui.output_ui("conditional"),
        ui.input_action_button("save", "Salva lo spettro"),
        ui.output_text('info_molecola'),
        ui.output_plot("spettro_plot"),
        #ui.input_dark_mode(mode="dark"),
    )

@module.server
def inserimento_server(input, output, session, Spettro, spettri, fonti):

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
    
    @render.ui
    @reactive.event(input.file_upload)
    def conditional():
        fontee = fonte_spettri()
        
        nome_file = session.spettro_oggetto.return_nome_file()
        namelist = nome_file.split("_")
        
        nome_molecola = namelist[2][3:].upper()
        data_creazione_spettro = namelist[1]
        tipo_supporto = namelist[3].split(".")[0].lower()
        if (tipo_supporto != "atr" and tipo_supporto != "nujol"):
            tipo_supporto = ""

        tipo_prova = namelist[2][:3].lower()
        if (tipo_prova == "inc"):
            tipo_prova = "Incognita"
        elif (tipo_prova == "std"):        
            tipo_prova = "Standard"
        else:
            tipo_prova = ""
        
        return (
            ui.card(
                ui.input_text(
                    "nome_molecola",
                    "Inserisci il nome della molecola",
                    value = f"{nome_molecola}",
                ),
                ui.input_date(
                    "data_creazione_spettro",
                    "Inserisci la data di creazione dello spettro",
                    value = f"{data_creazione_spettro}"
                ),
                ui.input_select(
                    "tipo_supporto",
                    "Seleziona il supporto utilizzato",
                    choices = ["ATR", "Nujol"],
                    selected = f"{tipo_supporto}"
                ),
                ui.input_select(
                    "tipo_prova",
                    "Seleziona il tipo di prova",
                    choices = ["Incognita", "Sperimentale"],
                    selected = f"{tipo_prova}"
                ),
                ui.input_select(
                    "fonte",
                    "Seleziona la fonte dello spettro",
                    choices = fontee
                ),
            )
        )

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

            fonte_spettro = input.fonte()

            risultato_salvataggio = spettro_oggetto.save_spettro(fonte_spettro)
            print(risultato_salvataggio)
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


    def fonte_spettri():
        fonte_spettri = fonti.get_fonti()

        # Converte da tuple a dizionario
        opzioni_fonti = {x[0]: x[1] for x in fonte_spettri}

        return opzioni_fonti