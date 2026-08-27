from shiny import module, ui, render, reactive
from datetime import datetime, date


@module.ui
def inserimento_ui():
    return (
        ui.input_file("file_upload", "Inserisci lo spettro", multiple=False),
        # Contenuto dinamico: appare solo dopo il caricamento di un file
        ui.output_ui("conditional"),
        # Il bottone parte disabilitato; viene abilitato solo dopo un caricamento valido
        ui.input_action_button("save", "Salva lo spettro", disabled=True),
        # ui.output_text("info_molecola"),
    )


@module.server
def inserimento_server(input, output, session, Spettro, spettri, fonti):
    """
    Argomenti iniettati:
      - Spettro   : classe che gestisce parsing e persistenza di un singolo spettro
      - spettri   : oggetto con metodi di rendering (es. render_plot)
      - fonti     : oggetto che espone get_fonti() per popolare il select delle fonti
    """

    # reactive.Value è il modo corretto per condividere stato mutabile tra
    # render/effect nello stesso modulo, al posto di session.attributo_custom
    spettro_oggetto = reactive.Value(None)

    # -------------------------------------------------------------------------
    # CARICAMENTO FILE
    # -------------------------------------------------------------------------

    @reactive.calc
    @reactive.event(input.file_upload)
    def spettro():
        """
        Punto di ingresso reattivo: si invalida solo quando cambia il file caricato.
        Crea l'oggetto Spettro, lo salva nel reactive.Value condiviso e
        restituisce i dati grezzi dello spettro (usati da plot e testo di debug).
        """
        file = input.file_upload()
        if not file or len(file) == 0:
            return None

        file_info = file[0]
        file_path, nome_file = file_info["datapath"], file_info["name"]

        try:
            obj = Spettro(file_path, nome_file)
            spettro_oggetto.set(obj)          # rende l'oggetto disponibile agli altri handler
            ui.update_action_button("save", disabled=False)
            return obj.get_dati_spettro()
        except Exception as e:
            spettro_oggetto.set(None)         # reset in caso di errore
            ui.notification_show(
                f"Errore nel caricamento: {e}",
                type="error",
                duration=4,
                close_button=True,
            )
            return None

    # -------------------------------------------------------------------------
    # FONTI
    # -------------------------------------------------------------------------

    @reactive.calc
    def fonti_disponibili():
        """
        Converte la lista di tuple (id, label) restituita da fonti.get_fonti()
        nel dizionario {id: label} atteso da ui.input_select.
        Wrappare in reactive.calc evita chiamate ripetute a get_fonti() ad ogni render.
        """
        raw = fonti.get_fonti()
        return {x[0]: x[1] for x in raw}

    # -------------------------------------------------------------------------
    # UI CONDIZIONALE
    # -------------------------------------------------------------------------

    @render.ui
    def conditional():
        if spettro() is None:
            return None

        obj = spettro_oggetto.get()
        if obj is None:
            return None

        # --- Parsing del nome file per pre-popolare il form ---
        nome_file = obj.return_nome_file()
        parts = nome_file.split("_")

        nome_molecola = parts[2][3:].upper() if len(parts) > 2 else ""
        data_creazione = _parse_date(parts[1]) if len(parts) > 1 else date.today()

        tipo_supporto_raw = parts[3].split(".")[0].lower() if len(parts) > 3 else ""
        tipo_supporto = (
            tipo_supporto_raw.capitalize()
            if tipo_supporto_raw in ("atr", "nujol")
            else "ATR"
        )

        tipo_prova_raw = parts[2][:3].lower() if len(parts) > 2 else ""
        tipo_prova_map = {"inc": "Incognita", "std": "Standard"}
        tipo_prova = tipo_prova_map.get(tipo_prova_raw, "Standard")

        return ui.layout_columns(
            # --- Colonna sinistra: form metadati ---
            ui.card(
                ui.card_header("Metadati spettro"),
                ui.input_text(
                    "nome_molecola",
                    "Inserisci il nome della molecola",
                    value=nome_molecola,
                ),
                ui.input_date(
                    "data_creazione_spettro",
                    "Inserisci la data di creazione dello spettro",
                    value=str(data_creazione),
                ),
                ui.input_select(
                    "tipo_supporto",
                    "Seleziona il supporto utilizzato",
                    choices=["ATR", "Nujol"],
                    selected=tipo_supporto,
                ),
                ui.input_select(
                    "tipo_prova",
                    "Seleziona il tipo di prova",
                    choices=["Incognita", "Standard"],
                    selected=tipo_prova,
                ),
                ui.input_select(
                    "fonte",
                    "Seleziona la fonte dello spettro",
                    choices=fonti_disponibili(),
                ),
            ),
            # --- Colonna destra: grafico ---
            ui.card(
                ui.card_header("Spettro"),
                ui.output_plot("spettro_plot"),
            ),
            col_widths=[4, 8],  # su 12 colonne: form più stretto, grafico più largo
        )

    # -------------------------------------------------------------------------
    # PLOT
    # -------------------------------------------------------------------------

    @render.plot
    def spettro_plot():
        """
        Dipende implicitamente da spettro(): si aggiorna automaticamente ad ogni
        nuovo caricamento senza @reactive.event, che qui sarebbe ridondante.
        """
        dati = spettro()
        if dati is None:
            return None
        try:
            return spettri.render_plot(dati)
        except Exception as e:
            ui.notification_show(
                f"Errore nel rendering del grafico: {e}",
                type="error",
                duration=4,
                close_button=True,
            )
            return None

    # -------------------------------------------------------------------------
    # DEBUG
    # -------------------------------------------------------------------------

    # @render.text
    # def info_molecola():
    #     """Mostra i dati grezzi dello spettro; utile in fase di sviluppo."""
    #     dati = spettro()
    #     return str(dati) if dati is not None else "Nessun dato disponibile"

    # -------------------------------------------------------------------------
    # SALVATAGGIO
    # -------------------------------------------------------------------------

    @reactive.effect
    @reactive.event(input.save)
    def save():
        """
        Si attiva solo al click del bottone "Salva".
        Controlla i duplicati nel DB prima di procedere al salvataggio,
        e notifica l'utente dell'esito in entrambi i casi.
        """
        obj = spettro_oggetto.get()
        if obj is None:
            # Caso difensivo: non dovrebbe accadere perché il bottone
            # è disabilitato finché spettro_oggetto è None
            ui.notification_show(
                "Errore: nessun spettro caricato.",
                type="error",
                duration=4,
                close_button=True,
            )
            return

        try:
            if obj.check_duplicati_db():
                ui.notification_show(
                    "Spettro già presente nel DB.",
                    type="error",
                    duration=4,
                    close_button=False,
                )
                ui.update_action_button("save", disabled=True)
                return

            # input.fonte() legge il valore corrente del select generato
            # da conditional(); è disponibile perché save() viene chiamato
            # solo dopo che l'utente ha interagito con il form
            risultato = obj.save_spettro(input.fonte())
            ui.notification_show(
                risultato.get("message", "Salvataggio completato."),
                type=risultato.get("type", "success"),
                duration=4,
            )
        except Exception as e:
            ui.notification_show(
                f"Errore durante il salvataggio: {e}",
                type="error",
                duration=4,
            )


# =============================================================================
# UTILITY (livello modulo, non server)
# =============================================================================

def _parse_date(date_string: str) -> date:
    """
    Converte una stringa in formato YYYY-MM-DD in un oggetto date.
    Restituisce la data odierna se il formato non è valido,
    garantendo un tipo di ritorno sempre consistente (mai una stringa).
    """
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        return date.today()




# from shiny import module, ui, render, reactive
# from datetime import datetime, date

# # IR_2022-03-30_STDMETILPIDROSSIBENZOATO_ATR.dx

# @module.ui
# def inserimento_ui():
#     return (
#         ui.input_file("file_upload", "Inserisci lo spettro", multiple=False),
#         ui.output_ui("conditional"),
#         ui.input_action_button("save", "Salva lo spettro"),
#         ui.output_plot("spettro_plot"),
#         ui.output_text('info_molecola'),
#         #ui.input_dark_mode(mode="dark"),
#     )

# @module.server
# def inserimento_server(input, output, session, Spettro, spettri, fonti):

#     # Legge il file e restituisce i dati dello spettro
#     @reactive.calc
#     @reactive.event(input.file_upload)
#     def spettro():
#         file = input.file_upload()
#         if not file or len(file) == 0:
#             return None  # Nessun file selezionato

#         file_info = file[0]
#         file_path, nome_file = file_info['datapath'], file_info['name']

#         try:
#             session.spettro_oggetto = Spettro(file_path, nome_file)
#             data = session.spettro_oggetto.get_dati_spettro()

#             # Abilita il bottone "save"
#             ui.update_action_button("save", disabled=False)

#             return data

#         except Exception as e:
#             return f"Errore nel caricamento: {e}"


#     # Renderizza i dati della molecola per debug
#     @render.text
#     @reactive.event(input.file_upload)
#     def info_molecola():
#         return spettro() or "Nessun dato disponibile"

#     @render.ui
#     @reactive.event(input.file_upload)
#     def conditional():
#         fontee = fonte_spettri()

#         nome_file = session.spettro_oggetto.return_nome_file()
#         namelist = nome_file.split("_")

#         nome_molecola = namelist[2][3:].upper()

#         data_creazione_spettro = is_valid_date(namelist[1])
#         tipo_supporto = namelist[3].split(".")[0].lower()
#         if (tipo_supporto != "atr" and tipo_supporto != "nujol"):
#             tipo_supporto = ""

#         tipo_prova = namelist[2][:3].lower()
#         if (tipo_prova == "inc"):
#             tipo_prova = "Incognita"
#         elif (tipo_prova == "std"):
#             tipo_prova = "Standard"
#         else:
#             tipo_prova = ""

#         return (
#             ui.card(
#                 ui.input_text(
#                     "nome_molecola",
#                     "Inserisci il nome della molecola",
#                     value = f"{nome_molecola}",
#                 ),
#                 ui.input_date(
#                     "data_creazione_spettro",
#                     "Inserisci la data di creazione dello spettro",
#                     value = f"{data_creazione_spettro}"
#                 ),
#                 ui.input_select(
#                     "tipo_supporto",
#                     "Seleziona il supporto utilizzato",
#                     choices = ["ATR", "Nujol"],
#                     selected = f"{tipo_supporto}"
#                 ),
#                 ui.input_select(
#                     "tipo_prova",
#                     "Seleziona il tipo di prova",
#                     choices = ["Incognita", "Standard"],
#                     selected = f"{tipo_prova}"
#                 ),
#                 ui.input_select(
#                     "fonte",
#                     "Seleziona la fonte dello spettro",
#                     choices = fontee
#                 ),
#             )
#         )

#     # Disegna il grafico dello spettro caricato
#     @render.plot
#     @reactive.event(input.file_upload)
#     def spettro_plot():
#         spettro_oggetto = getattr(session, "spettro_oggetto", None)
#         if not spettro_oggetto: # Nessuno spettro caricato
#             ui.notification_show(
#                 "Errore: nessun spettro caricato.",
#                 type="error",
#                 duration=4,
#                 close_button=True,
#             )
#             return

#         try:
#             dati_spettro = session.spettro_oggetto.get_dati_spettro()
#             if dati_spettro is None:
#                 return None
#             return spettri.render_plot(dati_spettro)

#         except Exception as e:
#             print(f"Errore nel rendering del grafico: {e}")
#             return None


#     # Funzione per verificare se la molecola è già nel DB
#     # controlla data e ora dello spettro
#     @reactive.effect
#     @reactive.event(input.save)
#     def save():
#         spettro_oggetto = getattr(session, "spettro_oggetto", None)
#         if not spettro_oggetto: # Nessuno spettro caricato
#             ui.notification_show(
#                 "Errore: nessun spettro caricato.",
#                 type="error",
#                 duration=4,
#                 close_button=True,
#             )
#             return

#         try:
#             esiste_gia = spettro_oggetto.check_duplicati_db()

#             if esiste_gia:
#                 ui.notification_show(
#                     "molecola già presente nel DB",
#                     type="error",
#                     duration=4,
#                     close_button=False,
#                 )
#                 ui.update_action_button("save", disabled = True)
#                 return None

#             fonte_spettro = input.fonte()

#             risultato_salvataggio = spettro_oggetto.save_spettro(fonte_spettro)
#             print(risultato_salvataggio)
#             ui.notification_show(
#                 risultato_salvataggio.get("message", "Salvataggio completato."),
#                 type=risultato_salvataggio.get("type", "success"),
#                 duration=4,
#             )

#         except Exception as e:
#             ui.notification_show(
#                 f"Errore durante il salvataggio: {e}",
#                 type="error",
#                 duration=4,
#             )


#     def fonte_spettri():
#         fonte_spettri = fonti.get_fonti()

#         # Converte da tuple a dizionario
#         opzioni_fonti = {x[0]: x[1] for x in fonte_spettri}

#         return opzioni_fonti



# def is_valid_date(date_string):
#     try:
#         return datetime.strptime(date_string, "%Y-%m-%d").date()
#     except ValueError:
#         print("c'è un errore: " , ValueError)
#         today = date.today().strftime("%Y-%m-%d")
#         return today