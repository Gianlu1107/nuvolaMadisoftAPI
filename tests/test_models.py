"""
Test per i modelli e la deserializzazione da dizionario.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuvola_api.models import (
    Alunno,
    Compito,
    MateriaVoti,
    VotoDettaglio,
    Assenza,
    Nota,
    ConteggioNotifiche,
    Pagamento,
)


class TestModels(unittest.TestCase):
    def test_alunno_from_dict(self):
        data = {
            "id": 12345,
            "nome": "LUCA",
            "cognome": "ROSSI",
            "nomeCompleto": "LUCA ROSSI",
            "attivoInAnnoScolasticoCorrente": True,
            "classe": "3B",
            "scuola": "SCUOLA MEDIA",
            "codiceFiscale": "RSSLCA10T15H501Z"
        }
        alunno = Alunno.from_dict(data)
        self.assertEqual(alunno.id, 12345)
        self.assertEqual(alunno.nome, "LUCA")
        self.assertEqual(alunno.cognome, "ROSSI")
        self.assertEqual(alunno.classe, "3B")
        self.assertTrue(alunno.attivo)

    def test_compito_list_description(self):
        data = {
            "docente": "BIANCHI MARCO",
            "materia": "ITALIANO",
            "dataAssegnazione": "2026-10-10",
            "dataConsegna": "2026-10-15",
            "descrizioneCompito": ["Esercizio 1", "Esercizio 2"],
            "classe": "3B",
            "classeId": 1024
        }
        compito = Compito.from_dict(data)
        self.assertEqual(compito.materia, "ITALIANO")
        self.assertEqual(compito.descrizione, "Esercizio 1\nEsercizio 2")

    def test_compito_string_description(self):
        data = {
            "docente": "VERDI LAURA",
            "materia": "MATEMATICA",
            "descrizioneCompito": "Ripasso equazioni",
            "classe": "3B"
        }
        compito = Compito.from_dict(data)
        self.assertEqual(compito.descrizione, "Ripasso equazioni")

    def test_materia_voti_media_float(self):
        data = {
            "id": 101,
            "materia": "ITALIANO",
            "conteggioVoti": 2,
            "media": "7.50",
            "voti": [
                {"data": "2026-10-01", "valutazione": "7"},
                {"data": "2026-10-05", "valutazione": "8"}
            ]
        }
        mv = MateriaVoti.from_dict(data)
        self.assertEqual(mv.conteggio_voti, 2)
        self.assertEqual(mv.media_float, 7.50)
        self.assertEqual(len(mv.voti), 2)

    def test_voto_dettaglio(self):
        data = {
            "data": "2026-10-05",
            "docente": "BIANCHI MARCO",
            "tipologia": "SCRITTO",
            "valutazione": "7½",
            "valutazioneMatematica": "7.50",
            "faMedia": True,
            "peso": "100%",
            "descrizione": "Verifica",
            "nomeMateria": "ITALIANO",
            "idMateria": 101,
            "idFrazioneTemporale": 1
        }
        v = VotoDettaglio.from_dict(data)
        self.assertEqual(v.valutazione, "7½")
        self.assertEqual(v.valore_numerico, 7.50)
        self.assertTrue(v.fa_media)

    def test_assenza(self):
        data = {
            "id": 301,
            "data": "2026-10-03",
            "turno": "TURNO MATTINO",
            "tipo": "RITARDO",
            "giustificata": True,
            "giustificabile": False,
            "ora": "08:35"
        }
        a = Assenza.from_dict(data)
        self.assertEqual(a.tipo, "RITARDO")
        self.assertTrue(a.giustificata)
        self.assertEqual(a.ora, "08:35")


if __name__ == "__main__":
    unittest.main()
