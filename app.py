from shiny import App, ui, render, reactive
from lib import spettri
from lib.spettro import Spettro
from lib import bande_gruppi_funzionali as bande_def
from lib import fonti
from lib import db
from lib import test
from lib import test2
from modules.gruppi_funzionali import *
from modules.visualizza import *
from modules.inserimento import *
from modules.singola_molecola import *
from modules.query import *
from modules.request import *
from modules.inserimento_multiplo import *
from modules.test import *
from modules.query_2 import *

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Inserimento",
        inserimento_ui("inserimento_ui"),
    ),
    ui.nav_panel(
        "Inserimento Multiplo",
        inserimento_multiplo_ui("inserimento_multiplo_ui")
    ),
    ui.nav_panel(
        "Visualizzazione",
        visualizza_ui("visualizza_ui"),
    ),
    ui.nav_panel(
        "Visualizza molecola",
        singola_molecola_ui("singola_molecola_ui")
    ),
    ui.nav_panel(
        "Gruppi funzionali",
        gruppi_funzionali_ui("gruppi_funzionali_ui"),
    ),
    ui.nav_panel(
        "Query DB",
        query_output_ui("query_output_ui"),
    ),
    ui.nav_panel(
        "Richieste Pub Chem",
        request_ui("request_ui"),
    ),
    ui.nav_panel(
        "Test Analisi Molecola",
        test_ui("test_ui")
    ),
    ui.nav_panel(
        "Modifica DB",
        insert_db_ui("insert_db")
    ),
    

    title="App with navbar",
    id="page"
)

def server(input, output, session):
    inserimento_server(
        "inserimento_ui",
        Spettro = Spettro,
        spettri = spettri,
        fonti = fonti
    )

    inserimento_multiplo_server(
        "inserimento_multiplo_ui",
        Spettro = Spettro,
        spettri = spettri,
        fonti = fonti
    )

    visualizza_server(
        "visualizza_ui",
        bande_def = bande_def,
        spettri = spettri
    )

    gruppi_funzionali_server(
        "gruppi_funzionali_ui", 
        bande_def=bande_def
    )

    singola_molecola_server(
        "singola_molecola_ui",
        bande_def = bande_def,
        spettri = spettri
    )

    query_output_server(
        "query_output_ui",
        db = db
    )

    request_server(
        "request_ui",
        bande_def = bande_def,
        spettri = spettri
    )

    test_server(
        "test_ui",
        test = test,
        spettri = spettri,
        bande_def = bande_def
    )

    insert_db_server(
        "insert_db",
        test = test2
    )

app = App(app_ui, server)