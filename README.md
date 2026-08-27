# IR Spectra Analysis App

Web application for archiving, comparing, and analyzing infrared (IR) spectra of
pharmaceutical substances.

Born as a lab tool: spectra produced by the spectrometer are uploaded in JCAMP-DX format,
the application archives them in a local database, and then lets you compare them against
each other, overlay functional group bands, and search for the molecules with the most
similar spectrum to a given one.

Built with [Shiny for Python](https://shiny.posit.co/py/), SQLite, and RDKit.

This project was part of my master's thesis, and I'm now working on improving it and fixing bugs as a side project.

---

## Requirements

- **Python 3.11** (the development environment uses 3.11.6)
- The dependencies listed in `requirements.txt`

## Installation

```bash
python -m venv venv
```

Activate the virtual environment — on Windows:

```bash
venv\Scripts\activate
```

on macOS and Linux:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

> **Note on dependencies.** `requirements.txt` doesn't pin versions yet. It also lists
> `plotly`, `shinywidgets`, and `scipy`, which the code no longer imports: these can be
> removed.

## Running the app

```bash
shiny run app.py --reload
```

The application opens at `http://127.0.0.1:8000`.

---

## How it works

The interface is split into tabs, one per function.

### Add Spectrum

Upload a single `.dx` file (JCAMP-DX). The application reads the file header, shows a
preview of the plot, and pre-fills the metadata by reading it from the **file name**, which
must follow this format:

```
TECHNIQUE_DATE_TESTTYPEMOLECULE_SUPPORT.dx
```

For example:

```
IR_2022-03-30_STDMETILPIDROSSIBENZOATO_ATR.dx
 │      │        │  │                   │
 │      │        │  │                   └── support: ATR or NUJOL
 │      │        │  └── molecule name
 │      │        └── test type: STD (standard) or INC (unknown)
 │      └── acquisition date, format YYYY-MM-DD
 └── technique
```

All four segments separated by `_` are required, and the date must be valid, otherwise the
upload is rejected with an explicit error message.

Before saving, the application checks whether the spectrum is already in the archive.

### Compare Spectra

Overlays two spectra on the same plot, with selectable colors, and lets you highlight the
absorption bands of chosen functional groups.

### View Molecule

Shows a single spectrum with its bands, adjustable band width via a slider, and the
bibliographic source of the data.

### Query DB

SQL console on the database, meant for quick inspection during development. Below the
console, the full table structure is shown.

> **Warning:** the console runs any SQL statement, including ones that modify or delete
> data. It's convenient locally, but it was disabled before publishing the application.

### Molecular Analysis

Shows the 2D molecular structure drawn by RDKit next to the spectrum, highlighting the
atoms and bonds that correspond to the selected functional group.

For the highlighting to work, two things are needed: the SMILES set on the spectrum
record, and the SMARTS pattern on the selected band (entered from the Edit DB tab).

### Molecular Similarity

Searches for the molecules with the closest spectrum to the selected one, using a
`NearestNeighbors` model with cosine distance. You can choose between number of results or
similarity threshold.

---

## Project structure

```
app.py                    UI composition and Shiny server registration
modello_ml.py             Spectral similarity model
setup_db.py                Database schema creation
struttura_db.py            Prints the structure of the existing database
conta_py.py                 Utility: code stats (functions, lines, comments)

lib/                      Data layer and domain logic
  spettro.py                Spettro class: JCAMP parsing, metadata, saving
  spettri.py                Spectrum reading and plot rendering
  bande_gruppi_funzionali.py  Bands and functional groups
  fonti.py                   Bibliographic source registry
  db.py                      Ad-hoc queries and schema introspection
  test2.py                   Writes to the registry (sources, groups, bands)

modules/                  One Shiny module per interface tab
testing/                  Automated tests (pytest)
documentazione/           Documentation for individual modules
```

## Database

SQLite, file `spettri.db` in the project root. Four tables:

| Table | Content |
|---|---|
| `spettri` | The spectra: name, date, test type, support, SMILES, and the x/y vectors in JSON |
| `bande_gruppi_funzionali` | The absorption bands: min–max range in cm⁻¹ and SMARTS pattern |
| `gruppi_funzionali` | The functional groups the bands belong to |
| `fonti` | The bibliographic sources for spectra and bands |

To inspect the existing database's schema:

```bash
python struttura_db.py
```

To create the schema from scratch, or check that an existing database contains all of it:

```bash
python setup_db.py
```

The script is idempotent (`CREATE TABLE IF NOT EXISTS`): running it on an already populated
database doesn't modify the data.

> **Note.** The column order in the `CREATE TABLE` statements is part of the contract:
> several parts of the code read rows by numeric index — `banda[2]` and `banda[3]` are `min`
> and `max` in `lib/spettri.py`, `banda[6]` is the SMARTS in `modules/analisi_molecola.py`.
> Changing it requires updating those modules too.

## Tests

```bash
pytest testing/
```

The suite covers `lib/spettri.py` (spectrum reading and rendering), working against a
temporary database, so it doesn't touch real data.

Four tests are currently red because they still test the `get_spettri()` interface from
before the refactor: they need to be realigned to the new signature, they don't signal a
problem with the application.

---

## Project status and next steps

The project is **under active development**. The visualization and analysis part is stable
and usable; the data import path is what's still being worked on and deserves attention
first.

### In progress

**Spectrum import.** This is the area with the most room for improvement, and the fixes are
interconnected:

- the input form pre-fills name, date, support, and test type, but on save the values read
  from the file name are reused: manual edits don't reach the database yet;
- duplicate detection compares name and date, so the same spectrum reimported under a
  different file name gets added twice. A hash of the data vector, with a `UNIQUE`
  constraint, would make the check independent of the name;
- the `smiles` field isn't written by the form and has to be filled in by hand; the PubChem
  module in `modules/request.py` already contains the logic to fetch it automatically from
  the molecule name.

**Archive normalization.** Two naming conventions coexist: the original one
(`ACIDOASCORBICO`) and the current composite-key one
(`ACIDOASCORBICO/STD/ATR/2023-05-10`). A one-off migration that populates the
`tipologia_prova` and `tipologia_spettrometro` columns — which already exist — and reduces
`nome` to just the molecule would considerably simplify the downstream code as well.

**Test coverage.** The current code covers `lib/spettri.py`, i.e. spectrum reading and
plot rendering. The goal is to extend testing to the rest of the backend, starting with
`lib/spettro.py`, which is the code that writes to the database (so it's the one where a
bug can insert wrong data into the archive).

### Backlog

- **Similarity model:** spectra acquired at a different resolution are currently excluded
  from the comparison; interpolating them onto a common wavenumber grid would recover all
  of them. Worth also evaluating per-sample normalization (SNV or min–max) before computing
  the distance.
- **Database access:** the file path is repeated across several modules; a single access
  point using `sqlite3.Row` would make the code independent of column order.
- **Cleanup:** remove the old versions left commented out in the modules (the history is
  already in git), the `partials/` folder, and the `spettri_old` table.
- **Disabled tabs:** bulk insert, functional groups, PubChem, and Edit DB are commented out
  in `app.py`. Edit DB in particular is the only interface for adding bands, sources, and
  functional groups: re-enabling it would avoid having to do it via SQL.
- **Tests:** extend coverage to `lib/spettro.py`, which is the import code, and add an
  automated run on push.
- **Repository:** drop `spettri.db` from version control in favor of schema and migrations,
  and add `centenario_principale.png` (the header image, currently untracked).

---

## License

To be determined.
