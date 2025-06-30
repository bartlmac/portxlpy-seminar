import sys
import pathlib

#  …/Arno/output in sys.path legen, damit compare_results importierbar ist
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import compare_results

def test_compare_results_no_diff():
    """Excel- und Python-Werte müssen identisch sein."""
    assert compare_results.main() is True
