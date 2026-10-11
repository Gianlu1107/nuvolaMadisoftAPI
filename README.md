# Nuvola API (Madisoft) — Specifiche Tecniche e Client REST

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](pyproject.toml)
[![Type Checking](https://img.shields.io/badge/types-mypy%20verified-informational.svg)](src/nuvola_api/py.typed)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Specifiche tecniche di protocollo e libreria client Python indipendente per l'integrazione e l'interazione programmatica con il registro elettronico Nuvola (Madisoft S.p.A.).  
Il progetto documenta analiticamente l'architettura RESTful retrostante all'applicazione mobile ufficiale (*Area Tutore e Studente*).

---

## Indice dei Contenuti

1. [Caratteristiche Architetturali](#1-caratteristiche-architetturali)
2. [Articolazione del Repository](#2-articolazione-del-repository)
3. [Installazione e Configurazione](#3-installazione-e-configurazione)
4. [Guida all'Integrazione (Python SDK)](#4-guida-allintegrazione-python-sdk)
5. [Interfaccia a Riga di Comando (nuvola-cli)](#5-interfaccia-a-riga-di-comando-nuvola-cli)
6. [Quadro Sinottico degli Endpoint](#6-quadro-sinottico-degli-endpoint)
7. [Considerazioni di Sicurezza e Riservatezza](#7-considerazioni-di-sicurezza-e-riservatezza)
8. [Note Legali e Conformita](#8-note-legali-e-conformita)
9. [Licenza](#9-licenza)

---

## 1. Caratteristiche Architetturali

- **Autenticazione Diretta (Bypass SPID/CIE):** Interazione con l'endpoint REST nativo dell'app mobile con credenziali istituzionali primarie, consentendo l'automazione anche nei contesti scolastici in cui il portale browser impone l'accesso esclusivo tramite identity provider federati.
- **Zero Dipendenze Esterne:** Il client opera unicamente con la libreria standard di Python (`urllib`, `json`, `dataclasses`, `argparse`), garantendo compatibilita assoluta e footprint ridotto.
- **Gestione del Ciclo di Vita del Token:** Rinnovo automatico e trasparente del token JWT (durata 1800 secondi) tramite rotazione del `refreshToken`, con meccanismo di retry in caso di risposta `HTTP 401 Unauthorized`.
- **Persistenza Controllata di Sessione:** Memorizzazione atomica dei token su file protetto locale per preservare lo stato di autenticazione tra esecuzioni successive.
- **Modellazione dei Dati Tipizzata:** Dataclass per ogni entita didattica (Alunni, Compiti, Orario, Lezioni, Valutazioni con medie ponderate, Assenze, Note disciplinari e Pagamenti PagoPA).
- **Strumentazione CLI Completa:** Esecutore da terminale per consultare, filtrare o esportare i dati in formato tabellare o JSON.

---

## 2. Articolazione del Repository

```text
nuvolaMadisoftAPI/
├── src/nuvola_api/                   # Sorgenti del pacchetto Python
│   ├── __init__.py                   # Esportazione di classi, modelli ed eccezioni
│   ├── client.py                     # Implementazione del client REST e gestione token
│   ├── models.py                     # Modelli di dati fortemente tipizzati
│   ├── exceptions.py                 # Gerarchia formale delle eccezioni applicative
│   ├── cli.py                        # Punto di ingresso dell'eseguibile nuvola-cli
│   └── py.typed                      # Indicatore di conformita PEP 561 per static typing
├── docs/                             # Documentazione tecnica esaustiva
│   ├── API_REFERENCE.md              # Riferimento analitico di ogni endpoint e payload
│   ├── AUTHENTICATION.md             # Specifiche su JWT, RS256, refresh token e sessioni
│   └── ARCHITECTURE.md               # Architettura backend, sharding e envelope pattern
├── examples/                         # Esempi pratici di utilizzo
│   ├── basic_usage.py                # Consultazione base di studenti, compiti e voti
│   ├── session_caching.py            # Dimostrazione operativa del recupero da cache
│   ├── export_to_json.py             # Script di esportazione per backup e integrazioni
│   ├── curl_cheatsheet.sh            # Esempi di interrogazione mediante cURL
│   └── typescript/                   # Implementazione client di riferimento in TypeScript
│       ├── package.json
│       └── client.ts
├── tests/                            # Suite di test unitari offline
│   ├── test_client.py                # Test sul ciclo di vita del client e simulazione errori HTTP
│   └── test_models.py                # Test di deserializzazione e validazione dei modelli
├── .github/                          # Integrazione continua e template operativi
│   ├── workflows/ci.yml              # Pipeline di validazione su Python 3.8-3.12
│   └── ISSUE_TEMPLATE/               # Modelli strutturati per segnalazioni e proposte
├── .env.example                      # Schema per variabili d'ambiente opzionali
├── .gitignore                        # Criteri di esclusione per cache, credenziali e build
├── CONTRIBUTING.md                   # Norme di contribuzione e disciplina di sanificazione
├── SECURITY.md                       # Protocollo di divulgazione responsabile delle vulnerabilita
├── LICENSE                           # Termini della licenza MIT e disclaimer sui marchi
├── pyproject.toml                    # Configurazione standardizzata del packaging (PEP 517/621)
└── nuvola_api_client.py              # Script di ingresso alla radice per retrocompatibilita
```

---

## 3. Installazione e Configurazione

### 3.1 Requisiti di Sistema
- Python versione 3.8 o superiore.
- Nessuna libreria o pacchetto di terze parti richiesto per il runtime.

### 3.2 Installazione da Sorgente
```bash
git clone https://github.com/Gianlu1107/nuvolaMadisoftAPI.git
cd nuvolaMadisoftAPI
pip install .
```

Per installare contestualmente gli strumenti di test e verifica statica:
```bash
pip install -e ".[dev]"
```

### 3.3 Utilizzo Diretto Senza Installazione
E possibile invocare direttamente il modulo sorgente o lo script radice:
```bash
python3 nuvola_api_client.py --help
```

---

## 4. Guida all'Integrazione (Python SDK)

### 4.1 Inizializzazione ed Esecuzione Base
```python
from nuvola_api import NuvolaClient, NuvolaError

# Istanziazione del client con memorizzazione su file di sessione locale
client = NuvolaClient(
    username="mario.rossi",
    password="Password123!",
    session_file="nuvola_session.json"
)

# Autenticazione (eseguita solo se non e presente una sessione valida riutilizzabile)
if not client.is_authenticated():
    client.login()

try:
    # 1. Recupero degli studenti associati all'utenza
    alunni = client.get_alunni()
    for alunno in alunni:
        print(f"Alunno: {alunno.nome_completo} - Classe: {alunno.classe}")

        # 2. Interrogazione compiti per una data specifica (formato DD-MM-YYYY)
        compiti = client.get_compiti(alunno.id, "15-10-2026")
        for c in compiti:
            print(f"[{c.materia}] Docente: {c.docente}")
            print(f"Descrizione: {c.descrizione}")

        # 3. Consultazione dello storico delle valutazioni
        voti = client.get_tutti_voti(alunno.id)
        for v in voti:
            print(f"Data: {v.data[:10]} | Materia: {v.nome_materia} | Valutazione: {v.valutazione}")

except NuvolaError as err:
    print(f"Eccezione durante l'interazione con l'API: {err}")
```

### 4.2 Gestione della Gerarchia delle Eccezioni
La libreria definisce un albero formale di eccezioni per un controllo granulare del flusso:
- `NuvolaError`: Radice comune per ogni errore generato dalla libreria.
- `NuvolaNetworkError`: Errori di connettivita, risoluzione DNS o timeout di rete.
- `NuvolaAPIError`: Errori HTTP restituiti dal server applicativo.
  - `NuvolaAuthError`: Fallimento autenticazione, credenziali non valide o sessione decaduta (`HTTP 401`).
  - `NuvolaPermissionError`: Accesso negato per mancanza di privilegi sulla risorsa (`HTTP 403`).
  - `NuvolaNotFoundError`: Risorsa inesistente (`HTTP 404`).

---

## 5. Interfaccia a Riga di Comando (nuvola-cli)

Il pacchetto registra l'eseguibile da terminale `nuvola-cli`:

### Comandi Operativi
```bash
# Autenticazione iniziale e generazione del file di sessione
nuvola-cli login -u mario.rossi -p "Password123!"

# Rinnovo esplicito del token
nuvola-cli refresh

# Consultazione studenti
nuvola-cli alunni

# Consultazione compiti per data (DD-MM-YYYY, default: data odierna)
nuvola-cli compiti --alunno-id 12345 --data 15-10-2026

# Orario e materie del giorno
nuvola-cli orario --alunno-id 12345

# Archivio valutazioni
nuvola-cli voti --alunno-id 12345

# Registro presenze (assenze e ritardi)
nuvola-cli assenze --alunno-id 12345

# Calendario verifiche ed eventi di classe
nuvola-cli eventi --alunno-id 12345

# Situazione contributi scolastici e PagoPA
nuvola-cli pagamenti --alunno-id 12345
```

### Emissione Dati in Formato Macchina (JSON)
L'aggiunta del flag globale `--json` instrada l'output in formato JSON puro:
```bash
nuvola-cli compiti --alunno-id 12345 --json | jq .
```

---

## 6. Quadro Sinottico degli Endpoint

Tutte le richieste impiegano il prefisso base: `https://nuvola.madisoft.it/api-studente/v1`

| Metodo | Percorso | Funzione | Riferimento Tecnico |
|---|---|---|---|
| `POST` | `/login` | Autenticazione diretta credenziali primarie | [Documentazione](docs/API_REFERENCE.md#21-post-login) |
| `POST` | `/refresh-token` | Rinnovo sessione tramite `refresh_token` | [Documentazione](docs/API_REFERENCE.md#22-post-refresh-token) |
| `GET` | `/login-from-web` | Conversione cookie di sessione web in JWT | [Documentazione](docs/API_REFERENCE.md#23-get-login-from-web) |
| `GET` | `/alunni` | Elenco studenti associati all'utenza | [Documentazione](docs/API_REFERENCE.md#31-get-alunni) |
| `GET` | `/alunno/{id}/compito/elenco/{date}` | Compiti con scadenza per la data fornita | [Documentazione](docs/API_REFERENCE.md#41-get-alunnoidcompitoelencodate) |
| `GET` | `/alunno/{id}/argomento-lezione/elenco/{date}` | Orario giornaliero, docenti e argomenti | [Documentazione](docs/API_REFERENCE.md#42-get-alunnoidargomento-lezioneelencodate) |
| `GET` | `/alunno/{id}/eventi-classe` | Verifiche programmate e comunicazioni | [Documentazione](docs/API_REFERENCE.md#43-get-alunnoideventi-classe) |
| `GET` | `/alunno/{id}/frazioni-temporali` | Quadrimestri, trimestri e periodi attivi | [Documentazione](docs/API_REFERENCE.md#51-get-alunnoidfrazioni-temporali) |
| `GET` | `/alunno/{id}/frazione-temporale/{frazioneId}/voti/materie` | Medie e valutazioni sintetiche per materia | [Documentazione](docs/API_REFERENCE.md#52-get-alunnoidfrazione-temporalefrazioneidvotimaterie) |
| `GET` | `/alunno/{id}/voti` | Storico completo e cronologico delle prove | [Documentazione](docs/API_REFERENCE.md#54-get-alunnoidvoti) |
| `GET` | `/alunno/{id}/assenze` | Assenze, ritardi e uscite anticipate | [Documentazione](docs/API_REFERENCE.md#61-get-alunnoidassenze) |
| `GET` | `/alunno/{id}/note` | Note disciplinari e richiami | [Documentazione](docs/API_REFERENCE.md#62-get-alunnoidnote) |
| `GET` | `/alunno/{id}/notifiche/conteggio` | Conteggio numerico avvisi pendenti | [Documentazione](docs/API_REFERENCE.md#71-get-alunnoidnotificheconteggio) |
| `GET` | `/alunno/{id}/pagamenti` | Contributi per attivita e avvisi PagoPA | [Documentazione](docs/API_REFERENCE.md#72-get-alunnoidpagamenti) |

Per l'analisi dettagliata di ogni endpoint, consultare il [Manuale Completo di Riferimento delle API](docs/API_REFERENCE.md).

---

## 7. Considerazioni di Sicurezza e Riservatezza

- **Gestione dei Token di Sessione:** I dati presenti in `nuvola_session.json` permettono l'accesso alle informazioni personali e al rendimento scolastico dell'alunno. Il file deve essere protetto tramite permessi restrittivi nel file system locale (`chmod 600`) e non deve essere incluso nei sistemi di controllo versione.
- **Dati Fittizi nella Documentazione:** Tutti i nominativi, codici istituto, identificativi anagrafici e parametri fiscali presenti in questo repository sono rigorosamente fittizi e disaccoppiati da soggetti reali.
- **Rate Limiting Prudenziale:** L'infrastruttura backend e protetta da AWS CloudFront. Interrogazioni massive o ad alta frequenza possono innescare blocchi temporanei dell'indirizzo IP del client.

---

## 8. Note Legali e Conformita

Il presente progetto e una libreria autonoma e non ufficiale:
- Non e affiliato, autorizzato, sponsorizzato o gestito in alcun modo da **Madisoft S.p.A.**
- Il marchio denominativo "Nuvola" e di proprieta esclusiva di **Madisoft S.p.A.**
- L'utilizzo della libreria deve avvenire nel pieno rispetto dei Termini di Servizio del registro elettronico e della normativa vigente in materia di protezione dei dati personali (Regolamento UE 2016/679 - GDPR).

---

## 9. Licenza

Il software e distribuito secondo i termini della licenza open-source [MIT](LICENSE).
