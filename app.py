from shiny import App, ui, render, reactive
from lib import spettri
from lib.spettro import Spettro
from lib import bande_gruppi_funzionali as bande_def
from lib import fonti
from modules.gruppi_funzionali import *
from modules.visualizza import *
from modules.inserimento import *

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Inserimento",
        inserimento_ui("inserimento_ui"),
    ),
    ui.nav_panel(
        "Visualizzazione",
        visualizza_ui("visualizza_ui"),
    ),
    ui.nav_panel(
        "Gruppi funzionali",
        gruppi_funzionali_ui("gruppi_funzionali_ui"),
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

    visualizza_server(
        "visualizza_ui",
        bande_def = bande_def,
        spettri = spettri
    )

    gruppi_funzionali_server(
        "gruppi_funzionali_ui", 
        bande_def=bande_def
    )

app = App(app_ui, server)