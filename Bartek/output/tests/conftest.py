import pytest
import tempfile
import shutil
import os
import pandas as pd

@pytest.fixture(scope="session")
def temp_csv_dir(tmp_path_factory):
    # Erzeuge ein temporäres Verzeichnis für Testdaten
    tmpdir = tmp_path_factory.mktemp("csv_data")
    # Schreibe Minimalbeispiele für alle CSVs
    var_content = "Name,Wert\nAlter,42\n"
    tarif_content = "Tarif,Wert\nStandard,1.5\n"
    grenzen_content = "Grenze,Wert\nMax,1000\n"
    tafeln_content = "x/y,DAV1994_T_M,DAV1994_T_F,DAV2008_T_M,DAV2008_T_F\n0,0.01,0.02,0.03,0.04\n"
    (tmpdir / "var.csv").write_text(var_content, encoding="utf-8")
    (tmpdir / "tarif.csv").write_text(tarif_content, encoding="utf-8")
    (tmpdir / "grenzen.csv").write_text(grenzen_content, encoding="utf-8")
    (tmpdir / "tafeln.csv").write_text(tafeln_content, encoding="utf-8")
    yield tmpdir