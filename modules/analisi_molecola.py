from shiny import module, ui, reactive, render
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
import itertools

# ---------------------------------------------------------------------------
# Utility RDKit
# ---------------------------------------------------------------------------

def _molecola_da_smiles(smiles: str) -> Chem.Mol | None:
    """Restituisce la molecola RDKit o None se lo SMILES non è valido."""
    return Chem.MolFromSmiles(smiles)


def _disegna_molecola(mol: Chem.Mol, smarts: str = "") -> str:
    """Genera un SVG 400x400 della molecola, con evidenziazione opzionale via SMARTS."""
    d = rdMolDraw2D.MolDraw2DSVG(400, 400)

    if not smarts:
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
        return d.GetDrawingText()

    patt = Chem.MolFromSmarts(smarts)
    if patt is None:
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
        return d.GetDrawingText()

    hit_ats_groups = [list(match) for match in mol.GetSubstructMatches(patt)]
    hit_ats = list(itertools.chain.from_iterable(hit_ats_groups))

    hit_bonds = [
        mol.GetBondBetweenAtoms(group[b.GetBeginAtomIdx()], group[b.GetEndAtomIdx()]).GetIdx()
        for b in patt.GetBonds()
        for group in hit_ats_groups
    ]

    rdMolDraw2D.PrepareAndDrawMolecule(d, mol, highlightAtoms=hit_ats, highlightBonds=hit_bonds)
    return d.GetDrawingText()


def _smarts_da_banda(lista_bande: list, id_banda: int) -> str:
    """Cerca lo SMARTS corrispondente all'id_banda nella lista bande."""
    for banda in lista_bande:
        if int(banda[0]) == id_banda:
            return banda[6]
    return ""


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@module.ui
def test_ui():
    return ui.card(
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select("select_molecola", "Seleziona la molecola", choices=[]),
                ui.input_select(
                    "select_fonte",
                    "Seleziona la fonte delle bande",
                    choices=["Cavrini et al."],
                ),
                ui.input_checkbox_group("selectize_bande", "Seleziona i gruppi da visualizzare:", choices=[]),
                ui.input_checkbox_group("selectize_bande_new", "Seleziona le bande da visualizzare:", choices=[]),
                ui.input_slider("slider_bande", "Seleziona la larghezza delle bande singole", 0, 50, 10),
                ui.input_action_button("visualizza_molecola", "Visualizza la molecola"),
            ),
            ui.layout_columns(
                ui.output_plot("spettro_selezionato_plot", fill=False),
                ui.output_ui("molecule_viewer"),
            ),
        )
    )


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

@module.server
def test_server(input, output, session, test, spettri, bande_def):

    # -- Stato reattivo ---------------------------------------------------

    _molecole: reactive.Value[list] = reactive.value([])
    _bande: reactive.Value[list] = reactive.value([])
    _spettro_corrente: reactive.Value[dict | None] = reactive.value(None)

    # -- Sync select / checkbox -------------------------------------------

    @reactive.effect
    def _sync_dati_iniziali():
        molecole = spettri.get_spettri_con_smiles()
        _molecole.set(molecole)
        _bande.set(bande_def.get_all_gruppi_funzionali())
        ui.update_select(
            "select_molecola",
            choices={str(id_): name for id_, name, _ in molecole},
        )

    @reactive.effect
    def _sync_gruppi():
        gruppi = bande_def.get_gruppi_new()
        ui.update_checkbox_group("selectize_bande", choices={x[0]: x[1] for x in gruppi})

    @reactive.effect
    @reactive.event(input.selectize_bande)
    def _sync_bande_per_gruppo():
        bande = bande_def.get_gruppi_funzionali_selezionati_new(input.selectize_bande())
        ui.update_checkbox_group("selectize_bande_new", choices=bande)

    # -- Aggiornamento stato al click -------------------------------------

    @reactive.effect
    @reactive.event(input.visualizza_molecola)
    def _aggiorna_spettro_corrente():
        id_molecola = input.select_molecola()
        _spettro_corrente.set(spettri.get_spettro(id_molecola) if id_molecola else None)

    # -- Render -----------------------------------------------------------

    @render.plot
    def spettro_selezionato_plot():
        spettro = _spettro_corrente()
        if spettro is None:
            return None

        return spettri.render_plot(
            spettro,
            input.selectize_bande_new(),
            None,
            "red",
            None,
            input.slider_bande(),
        )

    @render.ui
    def molecule_viewer():
        spettro = _spettro_corrente()
        if spettro is None:
            return None

        id_molecola = int(input.select_molecola())
        smiles = next((m[2] for m in _molecole() if m[0] == id_molecola), None)
        if not smiles:
            return None

        mol = _molecola_da_smiles(smiles)
        if mol is None:
            return ui.HTML("<p>SMILES non valido</p>")

        smarts = ""
        if bande_selezionate := input.selectize_bande_new():
            smarts = _smarts_da_banda(_bande(), int(bande_selezionate[0]))

        return ui.HTML(_disegna_molecola(mol, smarts))




# from shiny import module, ui, reactive, render
# from rdkit import Chem
# from rdkit.Chem import Draw
# from rdkit.Chem.Draw import rdMolDraw2D
# import itertools

# @module.ui
# def test_ui():
#     return(
#         ui.card(
#             ui.layout_sidebar(
#                 ui.sidebar(
#                     ui.input_select(
#                         "select_molecola",
#                         "Seleziona la molecola",
#                         choices = []
#                     ),
#                     ui.input_select(
#                         "select_fonte",
#                         "Seleziona la fonte delle bande",
#                         choices = ["Cavrini et al."]
#                     ),
#                     ui.input_checkbox_group(  
#                         "selectize_bande",  
#                         "Seleziona i gruppi da visualizzare:",
#                         choices = [],  
#                     ),
#                     ui.input_checkbox_group(  
#                         "selectize_bande_new",  
#                         "Seleziona le bande da visualizzare:",
#                         choices = [],  
#                     ),
#                     ui.input_slider(
#                         "slider_bande",
#                         "Seleziona la larghezza delle bande singole",
#                         0, 50, 10
#                     ),
#                     ui.input_action_button(
#                         "visualizza_molecola",
#                         "Visualizza la molecola"
#                     ),
#                 ),
#                 ui.layout_columns(
#                     ui.output_plot(
#                         "spettro_selezionato_plot",
#                         fill = False
#                     ),
#                     ui.output_ui("molecule_viewer"),
#                 )
#             )
            
#         )
#     )

# @module.server
# def test_server(input, output, session, test, spettri, bande_def):
#     lista_molecole = reactive.value([])
#     lista_bande = reactive.value([])

#     @reactive.effect()
#     def _():
#         lista_molecole.set(spettri.get_spettri_con_smiles())
#         lista_bande.set(bande_def.get_all_gruppi_funzionali())

#         ui.update_select(
#             "select_molecola",
#             choices = {f"{id_}": f"{name}" for id_, name, smiles in lista_molecole()}
#         )

#     @render.ui
#     @reactive.event(input.visualizza_molecola)
#     def molecule_viewer():
#         # Prendi il valore SMILES dall'input dell'utente
#         id_molecola = int(input.select_molecola())
        
#         molecola = next((mol[2] for mol in lista_molecole() if mol[0] == id_molecola), None)
#         smarts = ""
#         if input.selectize_bande_new():
#             id_banda = int(input.selectize_bande_new()[0]) # Tuple ('2',) diventa 2
            
#             for banda in lista_bande():
#                 if int(banda[0]) == int(id_banda):
#                     smarts = banda[6]
            
#         # Genera la visualizzazione della molecola con evidenziazione
#         svg_content = generate_2d_image_with_highlight(molecola, smarts)
        
#         # Restituisci l'SVG come HTML
#         return ui.HTML(svg_content)
    

#     # Crea la checkbox per vedere le bande dei gruppi funzionali
#     # nella schermata di visualizzazione
#     @reactive.effect
#     def selectize_bande():
#         #gruppi_funzionali = bande_def.get_gruppi_funzionali(False)
#         gruppi_funzionali = bande_def.get_gruppi_new()

#         # Converte da tuple a dizionario
#         opzioni_bande = {x[0]: x[1] for x in gruppi_funzionali}
        
#         ui.update_checkbox_group("selectize_bande", choices=opzioni_bande)

#     # TEST
#     @reactive.effect
#     @reactive.event(input.selectize_bande)
#     def selectize_bande_new():
#         gruppi_funzionali = input.selectize_bande()

#         bande_gruppi = bande_def.get_gruppi_funzionali_selezionati_new(gruppi_funzionali)
        
#         ui.update_checkbox_group("selectize_bande_new", choices=bande_gruppi)


#     @render.plot
#     @reactive.event(input.visualizza_molecola)
#     def spettro_selezionato_plot():
#         id_molecola = input.select_molecola()

#         spettro_molecola = spettri.get_spettro(id_molecola)

#         # Recupera le bande selezionate
#         bande_selezionate = input.selectize_bande_new()
        
#         # Genera e restituisce il grafico
#         return spettri.render_plot(
#             spettro_molecola, 
#             bande_selezionate, 
#             None,
#             "red", 
#             None,
#             input.slider_bande()
#         )


#     # Funzione per generare l'immagine 2D con evidenziazione
#     def generate_2d_image_with_highlight(smiles: str, smarts):
#         print(smarts)
#         # Creiamo la molecola da SMILES
#         mol = Chem.MolFromSmiles(smiles)
#         if mol is None:
#             return "Invalid SMILES string"
        
#         if not smarts:
#             d = rdMolDraw2D.MolDraw2DSVG(400, 400)
#             rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
#             svg = d.GetDrawingText()
#             return svg
        
#         # Creiamo il pattern SMARTS
#         patt = Chem.MolFromSmarts(smarts)
        
#         # Troviamo la corrispondenza del pattern (gli atomi che corrispondono)
#         hit_ats_input = list(mol.GetSubstructMatches(patt))
        
#         hit_ats = []
#         for x in hit_ats_input:
#             hit_ats.append(convertTupleToList(x))

#         # Troviamo i legami da evidenziare
#         hit_bonds = []
#         for bond in patt.GetBonds():
#             for hit_at in hit_ats:
#                 aid1 = hit_at[bond.GetBeginAtomIdx()]
#                 aid2 = hit_at[bond.GetEndAtomIdx()]
#                 hit_bonds.append(mol.GetBondBetweenAtoms(aid1, aid2).GetIdx())
        
#         hit_ats = list(itertools.chain(*hit_ats))
#         # Crea un oggetto MolDraw2DSVG per generare il disegno SVG
#         d = rdMolDraw2D.MolDraw2DSVG(400, 400)  # Impostiamo una dimensione di 500x500 px per il disegno
        
#         # Prepara e disegna la molecola, evidenziando gli atomi e i legami
#         rdMolDraw2D.PrepareAndDrawMolecule(d, mol, highlightAtoms=hit_ats, highlightBonds=hit_bonds)
        
#         # Ottieni il disegno SVG come stringa
#         svg = d.GetDrawingText()
        
#         # Restituisci l'SVG
#         return svg




# def convertTupleToList(tuple):
#     newList = []
#     for x in tuple:
#         newList.append(x)

#     return newList
