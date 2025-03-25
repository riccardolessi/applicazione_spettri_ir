from shiny import ui, render, reactive, module
import requests

# Funzione per fare la chiamata API
def get_api_data(molecola):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecola}/json"
    response = requests.get(url)
    
    # Verifica se la chiamata è andata a buon fine
    if response.status_code == 200:
        return response.json()  # Restituisce i dati JSON ricevuti dalla API
    else:
        return {"errore": "Chiamata API fallita"}

# Logica UI
@module.ui
def request_ui():
    return(
        ui.input_text("input", "Inserisci la molecola da cercare nel db PubChem"),
        ui.input_action_button("cerca_molecola", "Cerca"),
        ui.output_text("result"),
    )

# Logica del server
@module.server
def request_server(input, output, session):
    @render.text
    @reactive.event(input.cerca_molecola)
    def result():
        data = get_api_data(input.input())
        return str(data)