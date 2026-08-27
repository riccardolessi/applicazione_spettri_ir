import pytest
import json
import sqlite3
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Backend non interattivo per i test

from unittest.mock import patch, MagicMock
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

# ---------------------------------------------------------------------------
# Setup: importa il modulo puntando a un DB temporaneo
# ---------------------------------------------------------------------------

from lib import spettri as sp  # adatta il path se necessario


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_temporaneo(tmp_path):
    """Crea un database SQLite temporaneo con dati di test."""
    db = tmp_path / "spettri.db"

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE fonti (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL
        );

        CREATE TABLE spettri (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            smiles TEXT,
            dati TEXT NOT NULL,
            fonte_spettri INTEGER,
            FOREIGN KEY (fonte_spettri) REFERENCES fonti(id)
        );

        INSERT INTO fonti VALUES (1, 'NIST');
        INSERT INTO fonti VALUES (2, 'SDBS');

        INSERT INTO spettri VALUES (
            1, 'Acetone', 'CC(C)=O',
            '{"x": [4000, 3000, 2000, 1000], "y": [0.9, 0.5, 0.8, 0.3]}',
            1
        );
        INSERT INTO spettri VALUES (
            2, 'Etanolo', 'CCO',
            '{"x": [4000, 3000, 2000, 1000], "y": [0.4, 0.2, 0.7, 0.6]}',
            2
        );
        INSERT INTO spettri VALUES (
            3, 'JSON corrotto', 'C',
            'QUESTO NON E JSON',
            NULL
        );
    """)
    conn.commit()
    conn.close()

    return db


@pytest.fixture(autouse=True)
def patch_db_path(db_temporaneo):
    """Sovrascrive db_path nel modulo con il database temporaneo."""
    with patch.object(sp, "db_path", str(db_temporaneo)):
        yield


@pytest.fixture
def spettro_acetone():
    """Dizionario spettro nel formato restituito da get_spettro."""
    return {
        "metadati": {"molecola": "Acetone"},
        "dati": {"x": [4000, 3000, 2000, 1000], "y": [0.9, 0.5, 0.8, 0.3]},
        "fonte_spettro": "NIST"
    }


@pytest.fixture
def spettro_etanolo():
    return {
        "metadati": {"molecola": "Etanolo"},
        "dati": {"x": [4000, 3000, 2000, 1000], "y": [0.4, 0.2, 0.7, 0.6]},
        "fonte_spettro": "SDBS"
    }


# ---------------------------------------------------------------------------
# Test: _check_db
# ---------------------------------------------------------------------------

class TestCheckDb:
    def test_db_esistente_non_solleva(self, db_temporaneo):
        with patch.object(sp, "db_path", str(db_temporaneo)):
            sp._check_db()  # non deve sollevare

    def test_db_mancante_solleva_file_not_found(self, tmp_path):
        path_inesistente = str(tmp_path / "non_esiste.db")
        with patch.object(sp, "db_path", path_inesistente):
            with pytest.raises(FileNotFoundError, match="non_esiste.db"):
                sp._check_db()


# ---------------------------------------------------------------------------
# Test: get_spettri
# ---------------------------------------------------------------------------

class TestGetSpettri:
    def test_ritorna_dizionario(self):
        result = sp.get_spettri()
        assert isinstance(result, dict)

    def test_chiavi_e_valori_sono_stringhe(self):
        result = sp.get_spettri()
        for k, v in result.items():
            assert isinstance(k, str)
            assert isinstance(v, str)

    def test_contiene_molecole_inserite(self):
        result = sp.get_spettri()
        assert "Acetone" in result.values()
        assert "Etanolo" in result.values()

    def test_ordinato_per_nome(self):
        result = sp.get_spettri()
        nomi = list(result.values())
        assert nomi == sorted(nomi)

    def test_need_smiles_ritorna_lista_di_tuple(self):
        result = sp.get_spettri(need_smiles=True)
        assert isinstance(result, list)
        assert all(isinstance(r, tuple) for r in result)

    def test_need_smiles_include_smiles(self):
        result = sp.get_spettri(need_smiles=True)
        smiles_values = [r[2] for r in result]
        assert "CC(C)=O" in smiles_values
        assert "CCO" in smiles_values

    def test_db_vuoto_ritorna_dizionario_vuoto(self, tmp_path):
        db_vuoto = tmp_path / "vuoto.db"
        conn = sqlite3.connect(db_vuoto)
        conn.execute("CREATE TABLE spettri (id INTEGER, nome TEXT, smiles TEXT, dati TEXT, fonte_spettri INTEGER)")
        conn.commit()
        conn.close()
        with patch.object(sp, "db_path", str(db_vuoto)):
            result = sp.get_spettri()
        assert result == {}


# ---------------------------------------------------------------------------
# Test: get_spettri_con_smiles
# ---------------------------------------------------------------------------

class TestGetSpettriConSmiles:
    def test_ritorna_lista_di_tuple(self):
        result = sp.get_spettri_con_smiles()
        assert isinstance(result, list)
        assert all(isinstance(r, tuple) and len(r) == 3 for r in result)

    def test_contiene_smiles_corretti(self):
        result = sp.get_spettri_con_smiles()
        smiles = [r[2] for r in result]
        assert "CC(C)=O" in smiles

    def test_db_mancante_solleva(self, tmp_path):
        with patch.object(sp, "db_path", str(tmp_path / "no.db")):
            with pytest.raises(FileNotFoundError):
                sp.get_spettri_con_smiles()


# ---------------------------------------------------------------------------
# Test: get_spettro
# ---------------------------------------------------------------------------

class TestGetSpettro:
    def test_ritorna_struttura_corretta(self):
        result = sp.get_spettro(1)
        assert "metadati" in result
        assert "dati" in result
        assert "fonte_spettro" in result
        assert "molecola" in result["metadati"]
        assert "x" in result["dati"]
        assert "y" in result["dati"]

    def test_nome_molecola_corretto(self):
        result = sp.get_spettro(1)
        assert result["metadati"]["molecola"] == "Acetone"

    def test_fonte_corretta(self):
        result = sp.get_spettro(1)
        assert result["fonte_spettro"] == "NIST"

    def test_dati_x_y_sono_liste(self):
        result = sp.get_spettro(1)
        assert isinstance(result["dati"]["x"], list)
        assert isinstance(result["dati"]["y"], list)

    def test_id_inesistente_solleva_value_error(self):
        with pytest.raises(ValueError, match="9999"):
            sp.get_spettro(9999)

    def test_id_come_stringa(self):
        result = sp.get_spettro("1")
        assert result["metadati"]["molecola"] == "Acetone"

    def test_json_corrotto_solleva_value_error(self):
        with pytest.raises(ValueError, match="corrotti"):
            sp.get_spettro(3)

    def test_fonte_nulla_accettata(self):
        # Spettro con fonte NULL (id=3, il JSON è corrotto ma testiamo con un nuovo record)
        with patch.object(sp, "db_path", sp.db_path):
            conn = sqlite3.connect(sp.db_path)
            conn.execute(
                "INSERT INTO spettri VALUES (4, 'TestNull', 'C', '{\"x\":[1], \"y\":[1]}', NULL)"
            )
            conn.commit()
            conn.close()
            result = sp.get_spettro(4)
            assert result["fonte_spettro"] is None

    def test_db_mancante_solleva_file_not_found(self, tmp_path):
        with patch.object(sp, "db_path", str(tmp_path / "no.db")):
            with pytest.raises(FileNotFoundError):
                sp.get_spettro(1)


# ---------------------------------------------------------------------------
# Test: render_plot
# ---------------------------------------------------------------------------

class TestRenderPlot:
    def test_ritorna_figura(self, spettro_acetone):
        import matplotlib.pyplot as plt
        fig = sp.render_plot(spettro_acetone)
        assert isinstance(fig, plt.Figure)

    def test_dati_none_ritorna_none(self):
        assert sp.render_plot(None) is None

    def test_dati_vuoti_ritorna_none(self):
        assert sp.render_plot({}) is None

    def test_dati_senza_x_ritorna_none(self):
        dati = {"metadati": {"molecola": "X"}, "dati": {"y": [1, 2]}}
        assert sp.render_plot(dati) is None

    def test_dati_senza_y_ritorna_none(self):
        dati = {"metadati": {"molecola": "X"}, "dati": {"x": [1, 2]}}
        assert sp.render_plot(dati) is None

    def test_con_spettro_confronto(self, spettro_acetone, spettro_etanolo):
        import matplotlib.pyplot as plt
        fig = sp.render_plot(spettro_acetone, spettro_confronto=spettro_etanolo)
        assert isinstance(fig, plt.Figure)
        ax = fig.axes[0]
        assert len(ax.lines) == 2  # due curve

    def test_titolo_senza_confronto(self, spettro_acetone):
        fig = sp.render_plot(spettro_acetone)
        assert "Acetone" in fig.axes[0].get_title()

    def test_titolo_con_confronto(self, spettro_acetone, spettro_etanolo):
        fig = sp.render_plot(spettro_acetone, spettro_confronto=spettro_etanolo)
        titolo = fig.axes[0].get_title()
        assert "Acetone" in titolo
        assert "Etanolo" in titolo

    def test_asse_x_invertito(self, spettro_acetone):
        fig = sp.render_plot(spettro_acetone)
        ax = fig.axes[0]
        xlim = ax.get_xlim()
        assert xlim[0] > xlim[1]  # x deve essere invertito

    def test_colore_molecola_applicato(self, spettro_acetone):
        fig = sp.render_plot(spettro_acetone, colore_molecola="red")
        linea = fig.axes[0].lines[0]
        assert linea.get_color() == "red"

    def test_bande_selezionate_aggiungono_spans(self, spettro_acetone):
        bande_mock = [("alcol", "Alcol", 3200, 3550)]
        with patch("spettri.bd.get_gruppi_funzionali_selezionati", return_value=bande_mock):
            fig = sp.render_plot(spettro_acetone, bande_selezionate=["alcol"])
        patches = fig.axes[0].patches
        assert len(patches) > 0

    def test_bande_none_nessuno_span(self, spettro_acetone):
        fig = sp.render_plot(spettro_acetone, bande_selezionate=None)
        assert len(fig.axes[0].patches) == 0


# ---------------------------------------------------------------------------
# Test: helper privati
# ---------------------------------------------------------------------------

class TestHelperPrivati:
    def test_allarga_banda(self):
        banda = ("id", "nome", 3300, 3400)
        risultato = sp._allarga_banda(banda, larghezza=10)
        assert risultato[2] == 3300 - 10 + 1  # 3291
        assert risultato[3] == 3400 + 10 - 1  # 3409

    def test_allarga_banda_non_modifica_originale(self):
        banda = ("id", "nome", 3300, 3400)
        sp._allarga_banda(banda, 5)
        assert banda[2] == 3300  # originale invariato

    def test_build_titolo_senza_confronto(self, spettro_acetone):
        titolo = sp._build_titolo(spettro_acetone, None)
        assert "Acetone" in titolo
        assert "molecola" in titolo.lower()

    def test_build_titolo_con_confronto(self, spettro_acetone, spettro_etanolo):
        titolo = sp._build_titolo(spettro_acetone, spettro_etanolo)
        assert "Acetone" in titolo
        assert "Etanolo" in titolo
        assert "molecole" in titolo.lower()

    def test_build_titolo_split_slash(self):
        dati = {"metadati": {"molecola": "Acetone/deuterato"}, "dati": {}}
        titolo = sp._build_titolo(dati, None)
        assert "deuterato" not in titolo
        assert "Acetone" in titolo

    def test_get_bande_none_ritorna_none(self):
        assert sp._get_bande(None, None) is None

    def test_get_bande_lista_vuota_ritorna_none(self):
        assert sp._get_bande([], None) is None

    def test_get_bande_con_larghezza(self):
        bande_mock = [("id", "nome", 3300, 3400)]
        with patch("spettri.bd.get_gruppi_funzionali_selezionati", return_value=bande_mock):
            result = sp._get_bande(["alcol"], larghezza_bande_singole=5)
        assert result[0][2] == 3300 - 5 + 1
        assert result[0][3] == 3400 + 5 - 1