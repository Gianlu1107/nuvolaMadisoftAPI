#!/usr/bin/env python3
"""
Dimostrazione del funzionamento della persistenza di sessione e del refresh token automatico.
Non richiede username e password se è già presente un file nuvola_session.json valido.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuvola_api import NuvolaClient


def main():
    session_file = "nuvola_session.json"
    print(f"Inizializzo client con file di sessione: {session_file}")
    client = NuvolaClient(session_file=session_file)

    if not os.path.exists(session_file):
        print(f"File {session_file} non trovato. Esegui prima examples/basic_usage.py per autenticarti.")
        return

    expires_at = client.session_data.get("expires_at", 0)
    now = time.time()
    diff = int(expires_at - now)

    print(f"Stato sessione salvata:")
    print(f"- ID Anagrafica: {client.session_data.get('idAnagrafica')}")
    print(f"- Codice Cliente (Scuola): {client.session_data.get('codiceCliente')}")
    if diff > 0:
        print(f"- Token JWT attuale valido per ancora: {diff} secondi (~{diff // 60} minuti)")
    else:
        print(f"- Token JWT attuale SCADUTO da {-diff} secondi.")

    print("\nRichiamo get_valid_token()...")
    token = client.get_valid_token()
    print("Token valido ottenuto con successo! (Prime 25 lettere):", token[:25] + "...")

    print("Interrogo l'elenco degli alunni usando il token valido...")
    alunni = client.get_alunni()
    print(f"Recuperati con successo {len(alunni)} studenti:")
    for a in alunni:
        print(f" - {a.nome_completo} (Classe {a.classe})")


if __name__ == "__main__":
    main()
