#!/usr/bin/env python3
"""
Esempio di esportazione completa dei dati scolastici (alunni, voti, compiti, assenze, note)
in un file JSON locale, utile per backup o integrazioni esterne (Home Assistant, Bot Telegram).
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuvola_api import NuvolaClient


def main():
    client = NuvolaClient()
    if not client.is_authenticated():
        print("Client non autenticato. Configura le credenziali o esegui il login.")
        sys.exit(1)

    alunni = client.get_alunni()
    if not alunni:
        print("Nessun alunno associato all'account.")
        return

    data_oggi = datetime.now().strftime("%d-%m-%Y")
    dati_export = {
        "timestamp_esportazione": datetime.now().isoformat(),
        "studenti": []
    }

    for alunno in alunni:
        print(f"Esportazione dati per {alunno.nome_completo} (ID: {alunno.id})...")
        compiti = client.get_compiti_raw(alunno.id, data_oggi)
        orario = client.get_argomenti_lezione_raw(alunno.id, data_oggi)
        voti = [v.raw for v in client.get_tutti_voti(alunno.id)]
        assenze = [a.raw for a in client.get_assenze(alunno.id)]
        note = [n.raw for n in client.get_note(alunno.id)]
        eventi = [e.raw for e in client.get_eventi_classe(alunno.id)]

        dati_export["studenti"].append({
            "profilo": alunno.raw,
            "compiti_oggi": compiti,
            "orario_oggi": orario,
            "tutti_i_voti": voti,
            "assenze": assenze,
            "note": note,
            "eventi_classe": eventi
        })

    output_filename = f"nuvola_backup_{data_oggi}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(dati_export, f, indent=2, ensure_ascii=False)

    print(f"\n[INFO] Dati esportati con successo nel file: {output_filename}")


if __name__ == "__main__":
    main()
