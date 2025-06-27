# tests/test_bxt.py

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # …\davag\08
sys.path.insert(0, str(ROOT))

from ausfunct import Bxt

def test_bxt_reference_case():
    result = Bxt(vs=100_000, age=40, sex="M", n=30, t=20, zw=12, tarif="KLV")
    expected = 0.04226001
    assert abs(result - expected) < 1e-8, f"Bxt() = {result}, erwartet {expected}"
