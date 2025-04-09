from shiny import ui, render, reactive, module
import requests

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image
import io
import base64
from htmltools import HTML
import itertools

# Logica UI
@module.ui
def request_ui():
    return(
        ui.input_text("input", "Inserisci la molecola da cercare nel db PubChem"),
        ui.input_action_button("cerca_molecola", "Cerca"),
        ui.output_text("result"),
        ui.input_text("smiles", "Inserisci la stringa SMILES:", value="CCO"),
        ui.input_text("smarts", "Inserisci la stringa SMARTS: "),
        ui.input_action_button("visualizza_molecola", "Visualizza la molecola"),
        ui.output_ui("molecule_viewer")
    )

# Logica del server
@module.server
def request_server(input, output, session, bande_def, spettri):
    @render.text
    @reactive.event(input.cerca_molecola)
    def result():
        if input.input():
            data = get_api_data(input.input())
            return str(data)
        else:
            return str("Non è stata inserita nessuna molecola")
    
    @render.ui
    @reactive.event(input.visualizza_molecola)
    def molecule_viewer():
        # Prendi il valore SMILES dall'input dell'utente
        smiles = input.smiles()
        smarts = input.smarts()

        # Genera la visualizzazione della molecola con evidenziazione
        svg_content = generate_2d_image_with_highlight(smiles, smarts)
        
        # Restituisci l'SVG come HTML
        return ui.HTML(svg_content)
    

# Funzione per fare la chiamata API
def get_api_data(molecola):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecola}/property/SMILES/txt"
    response = requests.get(url)
    
    # Verifica se la chiamata è andata a buon fine
    if response.status_code == 200:
        return response.text.strip()  # Restituisce i dati JSON ricevuti dalla API
    else:
        return {"errore": "Chiamata API fallita"}
    
# Funzione per generare l'immagine 2D con evidenziazione
def generate_2d_image_with_highlight(smiles: str, smarts):
    # Creiamo la molecola da SMILES
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "Invalid SMILES string"
    
    if not smarts:
        d = rdMolDraw2D.MolDraw2DSVG(500, 500)
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
        svg = d.GetDrawingText()
        return svg
    
    # Creiamo il pattern SMARTS
    patt = Chem.MolFromSmarts(smarts)
    
    # Troviamo la corrispondenza del pattern (gli atomi che corrispondono)
    hit_ats_input = list(mol.GetSubstructMatches(patt))
    
    hit_ats = []
    for x in hit_ats_input:
        hit_ats.append(convertTupleToList(x))

    # Troviamo i legami da evidenziare
    hit_bonds = []
    for bond in patt.GetBonds():
        for hit_at in hit_ats:
            aid1 = hit_at[bond.GetBeginAtomIdx()]
            aid2 = hit_at[bond.GetEndAtomIdx()]
            hit_bonds.append(mol.GetBondBetweenAtoms(aid1, aid2).GetIdx())
    
    hit_ats = list(itertools.chain(*hit_ats))
    # Crea un oggetto MolDraw2DSVG per generare il disegno SVG
    d = rdMolDraw2D.MolDraw2DSVG(500, 500)  # Impostiamo una dimensione di 500x500 px per il disegno
    
    # Prepara e disegna la molecola, evidenziando gli atomi e i legami
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol, highlightAtoms=hit_ats, highlightBonds=hit_bonds)
    
    # Ottieni il disegno SVG come stringa
    svg = d.GetDrawingText()
    
    # Restituisci l'SVG
    return svg


def convertTupleToList(tuple):
    newList = []
    for x in tuple:
        newList.append(x)

    return newList