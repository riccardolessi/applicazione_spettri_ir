from shiny import module, ui, reactive
from functools import partial
from rdkit import Chem

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def mostra_notifica(messaggio: str, tipo_notifica: str = "message", durata: int = 4) -> None:
    """Mostra una notifica Shiny all'utente."""
    ui.notification_show(messaggio, type=tipo_notifica, duration=durata)


def _notifica_errore(messaggio: str) -> None:
    mostra_notifica(messaggio, tipo_notifica="error")


def _notifica_successo(messaggio: str) -> None:
    mostra_notifica(messaggio)


def _smarts_valido(smarts: str) -> bool:
    """
    True se il pattern e' compilabile da RDKit.
    Uno SMARTS invalido non solleverebbe errori a runtime: la molecola
    verrebbe semplicemente disegnata senza evidenziazione, in silenzio.
    """
    return Chem.MolFromSmarts(smarts) is not None


def _gestisci_risultato(result: str) -> None:
    """Dispatch sul risultato restituito dal layer dati."""
    if result == "success":
        _notifica_successo("Record salvato con successo nel database")
    else:
        _notifica_errore(result)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@module.ui
def insert_db_ui():
    return ui.navset_pill_list(
        ui.nav_panel(
            "Gruppi Funzionali",
            ui.input_text("gruppo_funzionale", "Nome gruppo funzionale"),
            ui.input_text("smile_gruppo", "SMILES del gruppo funzionale"),
            ui.input_action_button("save_gf", "Salva"),
        ),
        ui.nav_panel(
            "Bande Gruppi Funzionali",
            ui.input_text("bande_gruppo_funzionale", "Nome Banda"),  # typo corretto
            ui.input_numeric("min_banda", "Minimo banda", 1, min=1, max=4000),
            ui.input_numeric("max_banda", "Massimo banda", 1, min=1, max=4000),
            ui.input_text(
                "smarts_banda",
                "SMARTS della sottostruttura",
                placeholder="es. [CX3]=[OX1]",
            ),
            ui.input_select("lista_gruppi_funzionali", "Seleziona il gruppo funzionale", choices=[]),
            ui.input_select("lista_fonte_bande", "Seleziona la fonte della banda", choices=[]),
            ui.input_action_button("save_bande_gf", "Salva"),
        ),
        ui.nav_panel(
            "Fonti",
            ui.input_text("nome_fonte", "Nome Fonte"),
            ui.input_action_button("save_fonti", "Salva"),
        ),
    )


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

@module.server
def insert_db_server(input, output, session, test):

    # -- Sync dei select --------------------------------------------------

    @reactive.effect
    def _sync_fonti():
        ui.update_select("lista_fonte_bande", choices=test.fonti())

    @reactive.effect
    def _sync_gruppi():
        ui.update_select("lista_gruppi_funzionali", choices=test.gruppi_funzionali())

    # -- Fonti ------------------------------------------------------------

    @reactive.effect
    @reactive.event(input.save_fonti)
    def _salva_fonte():
        nome = input.nome_fonte()
        if not nome:
            _notifica_errore("È necessario compilare tutti i campi")
            return
        _gestisci_risultato(test.salva_fonte(nome))

    # -- Gruppi funzionali ------------------------------------------------

    @reactive.effect
    @reactive.event(input.save_gf)
    def _salva_gruppo_funzionale():
        nome = input.gruppo_funzionale()
        if not nome:
            _notifica_errore("È necessario compilare tutti i campi")
            return
        _gestisci_risultato(
            test.salva_gruppo_funzionale(nome, input.smile_gruppo())
        )

    # -- Bande gruppi funzionali ------------------------------------------

    @reactive.effect
    @reactive.event(input.save_bande_gf)
    def _salva_banda():
        nome   = input.bande_gruppo_funzionale()
        minimo = input.min_banda()
        massimo = input.max_banda()
        gruppo = input.lista_gruppi_funzionali()
        fonte  = input.lista_fonte_bande()
        smarts = input.smarts_banda().strip()

        if not all([nome, minimo, massimo, gruppo, smarts]):
            _notifica_errore("È necessario compilare tutti i campi")
            return

        if massimo <= minimo:
            _notifica_errore("Il massimo della banda deve essere superiore al minimo")
            return

        if not _smarts_valido(smarts):
            _notifica_errore(f"Il pattern SMARTS '{smarts}' non è valido")
            return

        _gestisci_risultato(
            test.salva_banda_gruppo_funzionale(nome, minimo, massimo, gruppo, fonte, smarts)
        )



# from shiny import module, ui, reactive, render
# import pandas as pd

# # Funzione per mostrare notifiche
# def mostra_notifica(messaggio, tipo_notifica = "message", durata = 4):
#     ui.notification_show(
#         messaggio,
#         type = tipo_notifica,
#         duration= durata
#     )


# @module.ui
# def insert_db_ui():
#     return (
#         ui.navset_pill_list(  
#             ui.nav_panel(
#                 "Gruppi Funzionali",
#                 ui.input_text("gruppo_funzionale", "Nome gruppo funzionale"),
#                 ui.input_text("smile_gruppo", "SMILES del gruppo funzionale"),
#                 ui.input_action_button("save_gf", "Salva")
#             ),
#             ui.nav_panel(
#                 "Bande Gruppi Funzionali",
#                 ui.input_text("bange_gruppo_funzionale", "Nome Banda"),
#                 ui.input_numeric("min_banda", "Minimo banda", 1, min = 1, max = 4000),
#                 ui.input_numeric("max_banda", "Massimo banda", 1, min = 1, max = 4000),
#                 ui.input_select("lista_gruppi_funzionali", "Seleziona il gruppo funzionale", choices = []),
#                 ui.input_select("lista_fonte_bande", "Seleziona la fonte della banda", choices = []),
#                 ui.input_action_button("save_bande_gf", "Salva")
#             ),
#             ui.nav_panel(
#                 "Fonti",
#                 ui.input_text("nome_fonte", "Nome Fonte"),
#                 ui.input_action_button("save_fonti", "Salva")
#             )   
#         )
#     )

# @module.server
# def insert_db_server(input, output, session, test):
#     #-------------------
#     # Logica fonti
#     #-------------------

#     @reactive.effect
#     @reactive.event(input.save_fonti)
#     def _():
#         if input.nome_fonte():
#             print(f"salvato in fonti")
#             print(f"Nome fonte: {input.nome_fonte()}")
            
#             result = test.salva_fonte(input.nome_fonte())
            
#             if result == "success":
#                 mostra_notifica(
#                     "Record salvato con successo le DB"
#                 )
#             else :
#                 mostra_notifica(
#                     result,
#                     tipo_notifica = "error"
#                 )
#         else:
#             mostra_notifica(
#                 "E' necessario compilare tutti i campi",
#                 tipo_notifica = "error"
#             )


#     #-------------------
#     # Logica bande gruppi funzionali
#     #-------------------
#     @reactive.effect
#     def _():
#         fonti = test.fonti()
#         ui.update_select("lista_fonte_bande", choices = fonti)

#     # Inserimento nel select dei gruppi funzionali
#     @reactive.effect
#     def _():
#         bande_gf = test.gruppi_funzionali()
#         ui.update_select("lista_gruppi_funzionali", choices = bande_gf)

#     # Logica per gestire il bottone per le bande dei gruppi funzionali
#     @reactive.effect
#     @reactive.event(input.save_bande_gf)
#     def _():
#         if input.bange_gruppo_funzionale() and input.min_banda() and input.max_banda() and input.lista_gruppi_funzionali():
#             if (input.max_banda() <= input.min_banda()):
#                 mostra_notifica(
#                     "Il massimo della banda deve essere superiore al minimo",
#                     tipo_notifica = "error"
#                 )
#                 return None
            
#             print(f"salvato in bande gruppi funzionali")
#             print(f"nome banda: {input.bange_gruppo_funzionale()}")
#             print(f"min: {input.min_banda()}")
#             print(f"max: {input.max_banda()}")
#             print(f"id gruppo funzionale: {input.lista_gruppi_funzionali()}")
#             print(f"fonte: {input.lista_fonte_bande()}")
            
            
#             # Logica del DB
#             result = test.salva_banda_gruppo_funzionale(
#                 input.bange_gruppo_funzionale(),
#                 input.min_banda(),
#                 input.max_banda(),
#                 input.lista_gruppi_funzionali(),
#                 input.lista_fonte_bande()
#             )
            
#             if result == "success":
#                 mostra_notifica("Record salvato con successo nel database")
#             else :
#                 mostra_notifica(result, tipo_notifica = "error")
#         else:
#             mostra_notifica(
#                 "E' necessario compilare tutti i campi",
#                 tipo_notifica = "error"
#             )

#     #-------------------
#     # Logica gruppi funzionali
#     #-------------------

#     # Logica per gestire il bottone per i gruppi funzionali
#     @reactive.effect
#     @reactive.event(input.save_gf)
#     def _():
#         if input.gruppo_funzionale():
#             print(f"salvato in gruppi funzionali")
#             print(f"{input.gruppo_funzionale()} {input.smile_gruppo()}")
            
#             result = test.salva_gruppo_funzionale(input.gruppo_funzionale(), input.smile_gruppo())
            
#             if result == "success":
#                 mostra_notifica("Record salvato con successo nel database")
#             else :
#                 mostra_notifica(result, tipo_notifica = "error")
#         else:
#             mostra_notifica(
#                 "E' necessario compilare tutti i campi",
#                 tipo_notifica = "error"
#             )