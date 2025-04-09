from shiny import module, ui, reactive, render
import pandas as pd

# Funzione per mostrare notifiche
def mostra_notifica(messaggio, tipo_notifica = "message", durata = 4):
    ui.notification_show(
        messaggio,
        type = tipo_notifica,
        duration= durata
    )


@module.ui
def insert_db_ui():
    return (
        ui.navset_pill_list(  
            ui.nav_panel(
                "Gruppi Funzionali",
                ui.input_text("gruppo_funzionale", "Nome gruppo funzionale"),
                ui.input_text("smile_gruppo", "SMILES del gruppo funzionale"),
                ui.input_action_button("save_gf", "Salva")
            ),
            ui.nav_panel(
                "Bande Gruppi Funzionali",
                ui.input_text("bange_gruppo_funzionale", "Nome Banda"),
                ui.input_numeric("min_banda", "Minimo banda", 1, min = 1, max = 4000),
                ui.input_numeric("max_banda", "Massimo banda", 1, min = 1, max = 4000),
                ui.input_select("lista_gruppi_funzionali", "Seleziona il gruppo funzionale", choices = []),
                ui.input_select("lista_fonte_bande", "Seleziona la fonte della banda", choices = []),
                ui.input_action_button("save_bande_gf", "Salva")
            ),
            ui.nav_panel(
                "Fonti",
                ui.input_text("nome_fonte", "Nome Fonte"),
                ui.input_action_button("save_fonti", "Salva")
            )   
        )
    )

@module.server
def insert_db_server(input, output, session, test):
    #-------------------
    # Logica fonti
    #-------------------

    @reactive.effect
    @reactive.event(input.save_fonti)
    def _():
        if input.nome_fonte():
            print(f"salvato in fonti")
            print(f"Nome fonte: {input.nome_fonte()}")
            
            result = test.salva_fonte(input.nome_fonte())
            
            if result == "success":
                mostra_notifica(
                    "Record salvato con successo le DB"
                )
            else :
                mostra_notifica(
                    result,
                    tipo_notifica = "error"
                )
        else:
            mostra_notifica(
                "E' necessario compilare tutti i campi",
                tipo_notifica = "error"
            )


    #-------------------
    # Logica bande gruppi funzionali
    #-------------------
    @reactive.effect
    def _():
        fonti = test.fonti()
        ui.update_select("lista_fonte_bande", choices = fonti)

    # Inserimento nel select dei gruppi funzionali
    @reactive.effect
    def _():
        bande_gf = test.gruppi_funzionali()
        ui.update_select("lista_gruppi_funzionali", choices = bande_gf)

    # Logica per gestire il bottone per le bande dei gruppi funzionali
    @reactive.effect
    @reactive.event(input.save_bande_gf)
    def _():
        if input.bange_gruppo_funzionale() and input.min_banda() and input.max_banda() and input.lista_gruppi_funzionali():
            if (input.max_banda() <= input.min_banda()):
                mostra_notifica(
                    "Il massimo della banda deve essere superiore al minimo",
                    tipo_notifica = "error"
                )
                return None
            
            print(f"salvato in bande gruppi funzionali")
            print(f"nome banda: {input.bange_gruppo_funzionale()}")
            print(f"min: {input.min_banda()}")
            print(f"max: {input.max_banda()}")
            print(f"id gruppo funzionale: {input.lista_gruppi_funzionali()}")
            print(f"fonte: {input.lista_fonte_bande()}")
            
            
            # Logica del DB
            result = test.salva_banda_gruppo_funzionale(
                input.bange_gruppo_funzionale(),
                input.min_banda(),
                input.max_banda(),
                input.lista_gruppi_funzionali(),
                input.lista_fonte_bande()
            )
            
            if result == "success":
                mostra_notifica("Record salvato con successo nel database")
            else :
                mostra_notifica(result, tipo_notifica = "error")
        else:
            mostra_notifica(
                "E' necessario compilare tutti i campi",
                tipo_notifica = "error"
            )

    #-------------------
    # Logica gruppi funzionali
    #-------------------

    # Logica per gestire il bottone per i gruppi funzionali
    @reactive.effect
    @reactive.event(input.save_gf)
    def _():
        if input.gruppo_funzionale():
            print(f"salvato in gruppi funzionali")
            print(f"{input.gruppo_funzionale()} {input.smile_gruppo()}")
            
            result = test.salva_gruppo_funzionale(input.gruppo_funzionale(), input.smile_gruppo())
            
            if result == "success":
                mostra_notifica("Record salvato con successo nel database")
            else :
                mostra_notifica(result, tipo_notifica = "error")
        else:
            mostra_notifica(
                "E' necessario compilare tutti i campi",
                tipo_notifica = "error"
            )