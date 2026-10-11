#!/usr/bin/env python3
"""
Esempio base di utilizzo della libreria nuvola-api.
Mostra l'accesso al registro elettronico e l'estrazione di alunni, compiti e voti.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Assicura che la directory src sia nel sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuvola_api import NuvolaClient, NuvolaError


def main():
    username = os.getenv("NUVOLA_USERNAME")
    password = os.getenv("NUVOLA_PASSWORD")

    # Inizializzazione client (con file di cache di default 'nuvola_session.json')
    client = NuvolaClient(username=username, password=password)

    # Se non siamo già autenticati e non abbiamo credenziali, richiediamole a terminale
    if not client.is_authenticated():
        if not username:
            client.username = input("Inserisci username Nuvola: ").strip()
        if not password:
            import getpass
            client.password = getpass.getpass("Inserisci password: ").strip()

        print("Effettuo il login...")
        client.login()
        print("Login completato con successo!\n")

    try:
        # 1. Recupero degli studenti associati
        print("--- Studenti Associati ---")
        alunni = client.get_alunni()
        for alunno in alunni:
            print(f"[{alunno.id}] {alunno.nome_completo} - Classe: {alunno.classe} ({alunno.scuola})")

        if not alunni:
            print("Nessun alunno associato all'account.")
            return

        primo_alunno = alunni[0]
        data_oggi = datetime.now().strftime("%d-%m-%Y")

        # 2. Recupero dei compiti di oggi
        print(f"\n--- Compiti per il {data_oggi} ({primo_alunno.nome_completo}) ---")
        compiti = client.get_compiti(primo_alunno.id, data_oggi)
        if compiti:
            for c in compiti:
                print(f"• [{c.materia}] (Prof. {c.docente}): {c.descrizione}")
        else:
            print("Nessun compito registrato per oggi.")

        # 3. Recupero delle ultime valutazioni
        print(f"\n--- Ultime Valutazioni ({primo_alunno.nome_completo}) ---")
        voti = client.get_tutti_voti(primo_alunno.id)
        for v in voti[:5]:
            print(f"• {v.data[:10]} | {v.nome_materia}: Voto {v.valutazione} ({v.tipologia}) - Prof. {v.docente}")

    except NuvolaError as e:
        print(f"Errore Nuvola: {e}")


if __name__ == "__main__":
    main()
