"""
Unit test suite per nuvola_api.
"""

import sys
from pathlib import Path

# Aggiunge automaticamente src/ al path durante l'esecuzione dei test
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
