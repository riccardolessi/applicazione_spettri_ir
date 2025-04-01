from shiny import module, ui, reactive, render


from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image
import io
import base64
from htmltools import HTML
import itertools

@module.ui
def test_ui():
    return(
        ui.input_numeric(
            "id_molecola",
            "ID Molecola",
            1, min = 1, max = 1000
        ),
        ui.input_text(
            "smiles",
            "Inserisci lo Smiles della molecola"
        ),
        ui.input_text(
            "smarts_gruppo",
            "Inserisci lo Smarts della parte di molecola di interesse"
        ),
        ui.input_numeric(
            "min",
            "Inserisci minimo della banda",
            1, min = 1, max = 4000
        ),
        ui.input_numeric(
            "max",
            "Inserisci massimo della banda",
            1, min = 1, max = 4000
        ),
        ui.input_action_button(
            "visualizza_molecola",
            "Visualizza la molecola"
        ),
        ui.output_ui("molecule_viewer"),
        ui.output_plot("spettro_selezionato_plot")
    )

@module.server
def test_server(input, output, session, test):

    @render.ui
    @reactive.event(input.visualizza_molecola)
    def molecule_viewer():
        # Prendi il valore SMILES dall'input dell'utente
        molecola = "CC(=O)OC1=CC=CC=C1C(=O)O"
        smarts = input.smarts_gruppo()

        # Genera la visualizzazione della molecola con evidenziazione
        svg_content = generate_2d_image_with_highlight(molecola, smarts)
        
        # Restituisci l'SVG come HTML
        return ui.HTML(svg_content)
    
    @render.plot
    @reactive.event(input.visualizza_molecola)
    def spettro_selezionato_plot():
        min = input.min()
        max = input.max()
        banda = [min, max]
        fig = test.pippo(input.id_molecola(), banda)
        return fig


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

