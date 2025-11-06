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
        ui.card(
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_select(
                        "select_molecola",
                        "Seleziona la molecola",
                        choices = []
                    ),
                    # ui.input_text(
                    #     "smarts_gruppo",
                    #     "Seleziona lo Smarts"
                    # ),
                    ui.input_select(
                        "select_fonte",
                        "Seleziona la fonte delle bande",
                        choices = ["Cavrini et al."]
                    ),
                    ui.input_checkbox_group(  
                        "selectize_bande",  
                        "Seleziona i gruppi da visualizzare:",
                        choices = [],  
                    ),
                    ui.input_checkbox_group(  
                        "selectize_bande_new",  
                        "Seleziona le bande da visualizzare:",
                        choices = [],  
                    ),
                    ui.input_slider(
                        "slider_bande",
                        "Seleziona la larghezza delle bande singole",
                        0, 50, 10
                    ),
                    ui.input_action_button(
                        "visualizza_molecola",
                        "Visualizza la molecola"
                    ),
                ),
                ui.layout_columns(
                    ui.output_plot(
                        "spettro_selezionato_plot",
                        fill = False
                    ),
                    ui.output_ui("molecule_viewer"),
                )
            )
            
        )
    )

@module.server
def test_server(input, output, session, test, spettri, bande_def):
    lista_molecole = reactive.value([])
    lista_bande = reactive.value([])

    @reactive.effect()
    def _():
        lista_molecole.set(spettri.get_spettri(True))
        lista_bande.set(bande_def.get_all_gruppi_funzionali())

        ui.update_select(
            "select_molecola",
            choices = {f"{id_}": f"{name}" for id_, name, smiles in lista_molecole()}
        )

    @render.ui
    @reactive.event(input.visualizza_molecola)
    def molecule_viewer():
        # Prendi il valore SMILES dall'input dell'utente
        id_molecola = int(input.select_molecola())
        
        molecola = next((mol[2] for mol in lista_molecole() if mol[0] == id_molecola), None)
        smarts = ""
        if input.selectize_bande_new():
            id_banda = int(input.selectize_bande_new()[0]) # Tuple ('2',) diventa 2

            smarts = next((banda[6] for banda in lista_bande() if banda[0] == id_banda ), "")
            
        # Genera la visualizzazione della molecola con evidenziazione
        svg_content = generate_2d_image_with_highlight(molecola, smarts)
        
        # Restituisci l'SVG come HTML
        return ui.HTML(svg_content)
    

    # Crea la checkbox per vedere le bande dei gruppi funzionali
    # nella schermata di visualizzazione
    @reactive.effect
    def selectize_bande():
        #gruppi_funzionali = bande_def.get_gruppi_funzionali(False)
        gruppi_funzionali = bande_def.get_gruppi_new()

        # Converte da tuple a dizionario
        opzioni_bande = {x[0]: x[1] for x in gruppi_funzionali}
        
        ui.update_checkbox_group("selectize_bande", choices=opzioni_bande)

    # TEST
    @reactive.effect
    @reactive.event(input.selectize_bande)
    def selectize_bande_new():
        gruppi_funzionali = input.selectize_bande()

        bande_gruppi = bande_def.get_gruppi_funzionali_selezionati_new(gruppi_funzionali)
        
        ui.update_checkbox_group("selectize_bande_new", choices=bande_gruppi)


    @render.plot
    @reactive.event(input.visualizza_molecola)
    def spettro_selezionato_plot():
        id_molecola = input.select_molecola()

        spettro_molecola = spettri.get_spettro(id_molecola)

        # Recupera le bande selezionate
        bande_selezionate = input.selectize_bande_new()
        
        # Genera e restituisce il grafico
        return spettri.render_plot(
            spettro_molecola, 
            bande_selezionate, 
            None,
            "red", 
            None,
            input.slider_bande()
        )


    # Funzione per generare l'immagine 2D con evidenziazione
    def generate_2d_image_with_highlight(smiles: str, smarts):
        print(smarts)
        # Creiamo la molecola da SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return "Invalid SMILES string"
        
        if not smarts:
            d = rdMolDraw2D.MolDraw2DSVG(200, 200)
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
        d = rdMolDraw2D.MolDraw2DSVG(200, 200)  # Impostiamo una dimensione di 500x500 px per il disegno
        
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
