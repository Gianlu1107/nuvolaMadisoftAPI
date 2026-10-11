#!/usr/bin/env python3
"""
Compatibilità retroattiva per importare NuvolaClient direttamente dalla radice.
Reindirizza al pacchetto src/nuvola_api.
"""

import sys
from pathlib import Path

# Aggiunge src al sys.path se necessario
src_path = str(Path(__file__).resolve().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from nuvola_api import NuvolaClient, NuvolaError, NuvolaAuthError, __version__

__all__ = ["NuvolaClient", "NuvolaError", "NuvolaAuthError", "__version__"]

if __name__ == "__main__":
    from nuvola_api.cli import main
    main()
