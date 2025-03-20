from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Draw import IPythonConsole
from rdkit.Chem import Draw
IPythonConsole.drawOptions.addAtomIndices = True
IPythonConsole.molSize = 300,300

# Dizionari dei gruppi funzionali e i loro range IR
ir_ranges = {
    "OH": (3200, 3600),  # Alcol
    "NH": (3300, 3500),  # Ammina
    "C=O": (1725, 1750), # Aldeide, chetone
    "C=C": (1600, 1650), # Alchene
    "C-H": (2850, 2960), # Alcano
    # Aggiungi altri gruppi funzionali e i loro intervalli
}

# Funzione per trovare i gruppi funzionali nella molecola
def find_functional_groups(mol):
    functional_groups = []
    if mol.HasSubstructMatch(Chem.MolFromSmarts("O")):  # Gruppo -OH
        functional_groups.append("OH")
    if mol.HasSubstructMatch(Chem.MolFromSmarts("N")):  # Gruppo -NH2
        functional_groups.append("NH")
    if mol.HasSubstructMatch(Chem.MolFromSmarts("C=O")):  # Gruppo -C=O (Aldeide/Ketone)
        functional_groups.append("C=O")
    if mol.HasSubstructMatch(Chem.MolFromSmarts("C=C")):  # Gruppo -C=C (Alchene)
        functional_groups.append("C=C")

    # Aggiungi altre strutture SMARTS per identificare altri gruppi
    return functional_groups

# SMILES della molecola
smiles = "C1=COC(=C1)CNC2=CC(=C(C=C2C(=O)O)S(=O)(=O)N)Cl"  # Furosemide

# Converto il SMILES in una molecola
mol = Chem.MolFromSmiles(smiles)

# Trovo i gruppi funzionali presenti nella molecola
groups_in_molecule = find_functional_groups(mol)

# Stampo i gruppi funzionali trovati e i loro intervalli IR
print("Gruppi funzionali trovati:", groups_in_molecule)
for group in groups_in_molecule:
    print(f"{group}: {ir_ranges.get(group)} cm⁻¹")
