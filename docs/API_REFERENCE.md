# Specifiche di Riferimento delle API di Nuvola (Madisoft S.p.A.)

Documentazione tecnica analitica dell'API REST esposta dal sistema di registro elettronico Nuvola.  
Tutti i payload, i parametri, gli identificativi e i nominativi presenti in questo documento sono rigorosamente fittizi e conformi alle norme sulla tutela della riservatezza.

---

## Indice Generale

- [1. Convenzioni Globali e Standard di Protocollo](#1-convenzioni-globali-e-standard-di-protocollo)
  - [1.1 Endpoint di Base e Intestazioni Obbligatorie](#11-endpoint-di-base-e-intestazioni-obbligatorie)
  - [1.2 Modello di Risposta a Involucro (Envelope Pattern)](#12-modello-di-risposta-a-involucro-envelope-pattern)
  - [1.3 Formati Temporali e Parametro contextAlunno](#13-formati-temporali-e-parametro-contextalunno)
- [2. Modulo Autenticazione](#2-modulo-autenticazione)
  - [2.1 POST /login](#21-post-login)
  - [2.2 POST /refresh-token](#22-post-refresh-token)
  - [2.3 GET /login-from-web](#23-get-login-from-web)
- [3. Modulo Anagrafica Studenti](#3-modulo-anagrafica-studenti)
  - [3.1 GET /alunni](#31-get-alunni)
- [4. Modulo Calendario, Didattica e Compiti](#4-modulo-calendario-didattica-e-compiti)
  - [4.1 GET /alunno/{id}/compito/elenco/{date}](#41-get-alunnoidcompitoelencodate)
  - [4.2 GET /alunno/{id}/argomento-lezione/elenco/{date}](#42-get-alunnoidargomento-lezioneelencodate)
  - [4.3 GET /alunno/{id}/eventi-classe](#43-get-alunnoideventi-classe)
  - [4.4 GET /alunno/{id}/eventi-classe-materia](#44-get-alunnoideventi-classe-materia)
  - [4.5 GET /alunno/{id}/eventi-alunno](#45-get-alunnoideventi-alunno)
- [5. Modulo Valutazioni e Voti](#5-modulo-valutazioni-e-voti)
  - [5.1 GET /alunno/{id}/frazioni-temporali](#51-get-alunnoidfrazioni-temporali)
  - [5.2 GET /alunno/{id}/frazione-temporale/{frazioneId}/voti/materie](#52-get-alunnoidfrazione-temporalefrazioneidvotimaterie)
  - [5.3 GET /alunno/{id}/frazione-temporale/{frazioneId}/voti/materia/{materiaId}](#53-get-alunnoidfrazione-temporalefrazioneidvotimateriamateriaid)
  - [5.4 GET /alunno/{id}/voti](#54-get-alunnoidvoti)
- [6. Modulo Registro di Classe e Disciplina](#6-modulo-registro-di-classe-e-disciplina)
  - [6.1 GET /alunno/{id}/assenze](#61-get-alunnoidassenze)
  - [6.2 GET /alunno/{id}/note](#62-get-alunnoidnote)
- [7. Modulo Notifiche e Servizi Finanziari](#7-modulo-notifiche-e-servizi-finanziari)
  - [7.1 GET /alunno/{id}/notifiche/conteggio](#71-get-alunnoidnotificheconteggio)
  - [7.2 GET /alunno/{id}/pagamenti](#72-get-alunnoidpagamenti)
- [8. Trattamento degli Errori e Codici HTTP](#8-trattamento-degli-errori-e-codici-http)

---

## 1. Convenzioni Globali e Standard di Protocollo

### 1.1 Endpoint di Base e Intestazioni Obbligatorie
L'intera superficie di interfaccia per l'Area Tutore e Studente risiede all'indirizzo radice:
```
https://nuvola.madisoft.it/api-studente/v1
```

Per ogni operazione autenticata, il client deve trasmettere le seguenti intestazioni HTTP:
```http
Authorization: Bearer <TOKEN_JWT>
Accept: application/json
User-Agent: okhttp/4.9.2
```

L'intestazione `User-Agent` valorizzata a `okhttp/4.9.2` riflette l'identificativo del client mobile ufficiale Android e garantisce la compatibilita con i filtri di instradamento della Content Delivery Network (AWS CloudFront).

### 1.2 Modello di Risposta a Involucro (Envelope Pattern)
Gli endpoint restituiscono un involucro JSON normalizzato:
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [ ... ],
  "paginatore": null
}
```
- `valori`: Contiene il carico utile principale (array o dizionario dei dati richiesti).
- `opzioni`: Vettore di coppie chiave-valore esprimenti i vincoli di visibilita e autorizzazione configurati dall'amministrazione della singola scuola (es. abilitazione alla visualizzazione della media ponderata o possibilita di giustificare le assenze telematicamente).
- `listeValori`: Tabelle ausiliarie o mappe di decodifica (es. associazione `idClasse -> nomeClasse`).
- `paginatore`: Metadati di paginazione per collezioni ampie (solitamente `null` nelle interrogazioni circoscritte per data o studente).

### 1.3 Formati Temporali e Parametro contextAlunno
- **Parametri di percorso (URL Path):** Le date trasmesse nel path devono essere formattate rigorosamente secondo lo standard `DD-MM-YYYY` (es. `15-10-2026`). L'omissione o la formattazione divergente genera errori `HTTP 404` o `HTTP 500`.
- **Valori temporali JSON:** Le date e i timestamp restituiti nelle strutture dati adottano lo standard ISO 8601 con offset fuso orario esplicito (es. `2026-10-15T00:00:00+02:00`).
- **Orario delle lezioni:** Stringhe nel formato `HH:MM` su base 24 ore (es. `"08:15"`, `"13:15"`).
- **Parametro contextAlunno:** Nelle richieste relative alle risorse dello studente e opportuno appendere il parametro di query `?contextAlunno={alunnoId}` al fine di allineare il contesto di sessione lato server.

---

## 2. Modulo Autenticazione

### 2.1 POST /login
Esegue l'autenticazione originaria mediante il canale REST riservato ai client nativi. Consente l'accesso tramite credenziali alfanumeriche primarie senza interazione con identity provider esterni (SPID/CIE).

#### Richiesta HTTP
```http
POST /api-studente/v1/login HTTP/1.1
Host: nuvola.madisoft.it
Content-Type: application/json
Accept: application/json
User-Agent: okhttp/4.9.2

{
  "username": "mario.rossi",
  "password": "PasswordFittizia123!"
}
```

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3OTE3NDU3MTAsImV4cCI6MTc5MTc0NzUxMCwiaXNzIjoibnV2b2xhIiwidXVpZCI6ImQ0ZTVmNmE3LWI4YzktNDAxMi1hMzQ1LTY3ODlhYmNkZWYwMSIsInNoYXJkIjoiUk1JQzhBQjAwMSIsImFwcGxpY2F6aW9uZSI6IkFQUCIsImFuYWdyYWZpY2FfaWQiOiIxMDQyIn0.MOCK_SIGNATURE_STRING",
  "refreshToken": "7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b",
  "id": "f1a2b3c4-d5e6-47a8-9b0c-1d2e3f4a5b6c",
  "idAnagrafica": 1042,
  "nome": "MARIO",
  "cognome": "ROSSI",
  "aree": [
    {
      "ruolo": "tutore",
      "nome": "Area tutore",
      "link": "https://nuvola.madisoft.it/area-tutore"
    }
  ],
  "codiceCliente": "RMIC8AB001",
  "username": "mario.rossi",
  "dataScadenzaCredenziali": "2027-06-30T23:59:59+02:00",
  "richiesto2FA": false
}
```

---

### 2.2 POST /refresh-token
Consente il rinnovo del Bearer Token JWT mediante l'invio del token opaco di refresh.

#### Richiesta HTTP
> [AVVERTENZA CRITICA SULLA CONVENZIONE DEL CAMPO]  
> Il corpo della richiesta a `/refresh-token` richiede la chiave **`refresh_token` in notazione snake_case**, differentemente dalla risposta del login che impiega `refreshToken` in camelCase.

```http
POST /api-studente/v1/refresh-token HTTP/1.1
Host: nuvola.madisoft.it
Content-Type: application/json
Accept: application/json
User-Agent: okhttp/4.9.2

{
  "refresh_token": "7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b"
}
```

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3OTE3NDc1MTAsImV4cCI6MTc5MTc0OTMxMCwiaXNzIjoibnV2b2xhIn0.NEW_MOCK_SIGNATURE",
  "refreshToken": "8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c"
}
```

---

### 2.3 GET /login-from-web
Estrae un Bearer Token JWT a partire da una sessione browser preesistente autenticata tramite cookie `nuvola`.

#### Richiesta HTTP
```http
GET /api-studente/v1/login-from-web HTTP/1.1
Host: nuvola.madisoft.it
Cookie: nuvola=SESSION_COOKIE_VALUE
Accept: application/json
```

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.WEB_EXTRACTED_MOCK_TOKEN"
}
```

---

## 3. Modulo Anagrafica Studenti

### 3.1 GET /alunni
Elenca gli studenti formalmente associati al profilo genitore/tutore autenticato.

#### Richiesta HTTP
```http
GET /api-studente/v1/alunni HTTP/1.1
Host: nuvola.madisoft.it
Authorization: Bearer <TOKEN_JWT>
User-Agent: okhttp/4.9.2
```

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    {
      "id": 12345,
      "nome": "LUCA",
      "cognome": "ROSSI",
      "nomeCompleto": "LUCA ROSSI",
      "attivoInAnnoScolasticoCorrente": true,
      "classe": "3B",
      "scuola": "SCUOLA SECONDARIA DI PRIMO GRADO",
      "codiceFiscale": "RSSLCA10T15H501Z",
      "dataNascita": "2011-09-15T00:00:00+02:00"
    }
  ],
  "paginatore": null
}
```

---

## 4. Modulo Calendario, Didattica e Compiti

### 4.1 GET /alunno/{id}/compito/elenco/{date}
Recupera l'elenco dei compiti per casa la cui scadenza o consegna e prevista per la data indicata.

#### Parametri
- `{id}`: Identificativo numerico dell'alunno (es. `12345`).
- `{date}`: Data in formato `DD-MM-YYYY` (es. `15-10-2026`).
- Parametro query: `?contextAlunno=12345`

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": {
    "valori_classi_per_alunno": {
      "1024": "3B"
    }
  },
  "opzioni": [
    {
      "opzione": "compito_mostra_argomento_lezione",
      "impostazione": false
    }
  ],
  "valori": [
    {
      "docente": "BIANCHI MARCO",
      "materia": "ITALIANO",
      "nomeArgomento": null,
      "idArgomento": null,
      "dataAssegnazione": "2026-10-10T00:00:00+02:00",
      "dataConsegna": "2026-10-15T00:00:00+02:00",
      "descrizioneCompito": [
        "Grammatica: svolgere gli esercizi a pag. 142 n. 3, 4, 5 e ripasso analisi del periodo."
      ],
      "allegati": [],
      "classe": "3B",
      "classeId": 1024
    }
  ],
  "paginatore": null
}
```

> [NOTA TECNICA SUL PARSING DI descrizioneCompito]  
> Il campo `descrizioneCompito` puo assumere la forma di un vettore di stringhe (`List[str]`) oppure di una stringa scalare (`str`). Il client implementa un parser polimorfico in grado di normalizzare entrambe le varianti.

---

### 4.2 GET /alunno/{id}/argomento-lezione/elenco/{date}
Restituisce la scansione oraria della giornata scolastica con le discipline impartite, i docenti designati e i contenuti didattici svolti.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [
    {
      "opzione": "argomento_lezione_mostra_descrizione_estesa",
      "impostazione": false
    }
  ],
  "valori": [
    {
      "classe": "3B",
      "classeId": 1024,
      "isGruppoClasse": false,
      "ore": [
        {
          "numeroOra": 1,
          "inizioOra": "08:15",
          "fineOra": "09:15",
          "giorno": "2026-10-15T00:00:00+02:00",
          "argomenti": [
            {
              "id": 10101,
              "materia": "MATEMATICA",
              "docente": "VERDI LAURA",
              "tipo": "Lezione ordinaria",
              "nomeArgomento": "Equazioni di primo grado e problemi applicati",
              "annotazioni": null,
              "descrizioneEstesa": null,
              "compresenza": "",
              "allegati": [],
              "cofirme": [],
              "video_youtube": []
            }
          ]
        },
        {
          "numeroOra": 2,
          "inizioOra": "09:15",
          "fineOra": "10:15",
          "giorno": "2026-10-15T00:00:00+02:00",
          "argomenti": [
            {
              "id": 10102,
              "materia": "ITALIANO",
              "docente": "FERRARI DANIELA",
              "tipo": "Lezione ordinaria",
              "nomeArgomento": "Lettura ed analisi brano antologia pag. 88",
              "annotazioni": null,
              "descrizioneEstesa": null,
              "compresenza": "",
              "allegati": [],
              "cofirme": [],
              "video_youtube": []
            }
          ]
        }
      ]
    }
  ],
  "paginatore": null
}
```

---

### 4.3 GET /alunno/{id}/eventi-classe
Restituisce il calendario delle verifiche scritte o orali pianificate, delle uscite didattiche e delle comunicazioni formali alla classe.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    {
      "id": 20201,
      "tipo": "Avviso",
      "nome": "Geometria",
      "descrizione": "Verifica scritta sui teoremi fondamentali di Geometria",
      "dataInizio": "2026-10-20T00:00:00+02:00",
      "oraInizio": "10:15",
      "dataFine": "2026-10-20T00:00:00+02:00",
      "oraFine": "11:15",
      "docente": "ROMANO ENRICO",
      "annotazioni": null,
      "visto": true,
      "allegati": [],
      "linkVideo": [],
      "coloreSfondo": "FFFFFF",
      "coloreTesto": "000000",
      "coloreBordo": "000000",
      "idNotifica": null,
      "adesioneRichiesta": false,
      "scadenzaAdesione": null,
      "adesioneEspressa": null
    }
  ],
  "paginatore": null
}
```

---

### 4.4 GET /alunno/{id}/eventi-classe-materia
Fornisce la medesima struttura di `eventi-classe`, filtrando per singola disciplina.

### 4.5 GET /alunno/{id}/eventi-alunno
Fornisce gli eventi individuali afferenti in via esclusiva allo studente specificato.

---

## 5. Modulo Valutazioni e Voti

### 5.1 GET /alunno/{id}/frazioni-temporali
Restituisce l'articolazione temporale dell'anno scolastico definita dal piano dell'offerta formativa dell'istituto (Quadrimestri o Trimestri).

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    { "id": 1, "nome": "1° QUADRIMESTRE", "corrente": true },
    { "id": 2, "nome": "2° QUADRIMESTRE", "corrente": false },
    { "id": 3, "nome": "INTERO ANNO", "corrente": false }
  ],
  "paginatore": null
}
```

---

### 5.2 GET /alunno/{id}/frazione-temporale/{frazioneId}/voti/materie
Restituisce il prospetto sintetico per materia relativo al periodo selezionato, comprensivo della media aritmetica calcolata.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    {
      "id": 101,
      "materia": "ITALIANO",
      "conteggioVoti": 2,
      "media": "7.25",
      "tipo": null,
      "voti": [
        {
          "data": "2026-10-05T00:00:00+02:00",
          "valutazione": "7½"
        },
        {
          "data": "2026-09-22T00:00:00+02:00",
          "valutazione": "7"
        }
      ]
    }
  ],
  "paginatore": null
}
```

---

### 5.3 GET /alunno/{id}/frazione-temporale/{frazioneId}/voti/materia/{materiaId}
Restituisce il dettaglio esteso delle singole prove per una determinata disciplina, comprensivo di commenti didattici ed eventuali obiettivi di apprendimento.

---

### 5.4 GET /alunno/{id}/voti
Restituisce l'archivio cronologico completo di tutte le valutazioni attribuite all'alunno durante l'anno scolastico.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    {
      "data": "2026-10-05T00:00:00+02:00",
      "docente": "BIANCHI MARCO",
      "tipologia": "SCRITTO",
      "valutazione": "7½",
      "valutazioneMatematica": "7.50",
      "faMedia": true,
      "peso": "100%",
      "descrizione": "Verifica scritta di grammatica: proposizioni subordinate",
      "strumentoProva": null,
      "tipologiaSituazione": null,
      "risorseMobilitate": null,
      "autonomia": null,
      "continuita": null,
      "nomeObiettivo": null,
      "obiettivi": [],
      "nomeMateria": "ITALIANO",
      "idMateria": 101,
      "idFrazioneTemporale": 1
    }
  ],
  "paginatore": null
}
```

- `valutazione`: Espressione testuale del voto assegnato (`"8+"`, `"7½"`, `"6-"`, `"Non classificato"`).
- `valutazioneMatematica`: Valore in formato decimale normalizzato per il calcolo statistico (`"7.50"`).
- `faMedia`: Booleano che qualifica la prova come valutativa o formativa non concorrente alla media.
- `peso`: Coefficiente di ponderazione percentuale applicato alla prova (`"100%"`, `"50%"`).

---

## 6. Modulo Registro di Classe e Disciplina

### 6.1 GET /alunno/{id}/assenze
Recupera l'archivio delle assenze giornaliere, dei ritardi di ingresso e delle uscite anticipate.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [
    { "opzione": "assenza_mostra_turno", "impostazione": true },
    { "opzione": "assenze_abilita_giustificazioni", "impostazione": true },
    { "opzione": "assenza_abilita_gestione", "impostazione": false }
  ],
  "valori": [
    {
      "id": 301,
      "data": "2026-10-03T00:00:00+02:00",
      "turno": "TURNO MATTINO",
      "tipo": "RITARDO",
      "tipoAssenza": null,
      "giustificata": true,
      "giustificabile": false,
      "ora": "08:35"
    },
    {
      "id": 302,
      "data": "2026-09-28T00:00:00+02:00",
      "turno": "TURNO MATTINO",
      "tipo": "ASSENZA",
      "tipoAssenza": null,
      "giustificata": true,
      "giustificabile": false,
      "ora": null
    }
  ],
  "paginatore": null
}
```
Valori tassonomici del campo `tipo`: `"ASSENZA"`, `"RITARDO"`, `"USCITA_ANTICIPATA"`.

---

### 6.2 GET /alunno/{id}/note
Restituisce le annotazioni disciplinari e i richiami registrati dal personale docente.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    {
      "id": 401,
      "data": "2026-09-18T00:00:00+02:00",
      "docente": "BIANCHI MARCO",
      "registroDiClasse": true,
      "materia": "ITALIANO",
      "tipologia": "ALTRO TIPO DI NOTA",
      "descrizione": "Nota informativa: promemoria autorizzazione uscita didattica."
    }
  ],
  "paginatore": null
}
```

---

## 7. Modulo Notifiche e Servizi Finanziari

### 7.1 GET /alunno/{id}/notifiche/conteggio
Restituisce il riepilogo numerico degli avvisi e delle comunicazioni non ancora visualizzati.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "eventi": 1,
  "bacheche": 3
}
```

---

### 7.2 GET /alunno/{id}/pagamenti
Restituisce il registro degli obblighi di pagamento scolastici, contributi per attivita didattiche e avvisi PagoPA / Pago in Rete.

#### Risposta di Successo (HTTP 200 OK)
```json
{
  "listeValori": null,
  "opzioni": [],
  "valori": [
    {
      "id": "a1b2c3d4-1111-4444-8888-0123456789ab",
      "tassa": "Visita didattica del 25/03/2026 al Museo delle Scienze Naturali",
      "messaggioPerDestinatari": null,
      "rata": "rata unica",
      "dataScadenzaRata": "2026-03-25T00:00:00+01:00",
      "importo": "6,50 €",
      "statoPagamento": "PAGATO",
      "modalitaPagamento": "Pago in Rete",
      "dataPagamento": "2026-03-20T00:00:00+01:00",
      "allegatoAvvisoPagamento": "b2c3d4e5-2222-4444-8888-abcdef012345",
      "nomeAlunno": "LUCA"
    }
  ],
  "paginatore": null
}
```

---

## 8. Trattamento degli Errori e Codici HTTP

| Codice di Stato | Corpo di Risposta Tipico | Descrizione Tecnica e Rimedio |
|---|---|---|
| `400 Bad Request` | `{"code": 400, "message": "Bad Request"}` | Struttura JSON malformata o parametri obbligatori omessi nel body. |
| `401 Unauthorized` | `{"code": 401, "message": "Full authentication is required..."}` | Token Bearer assente, scaduto o privo di firma valida. Richiede l'esecuzione di `/refresh-token`. |
| `401 Unauthorized` | `{"code": 401, "message": "Username o password errate"}` | Credenziali di accesso non valide fornite a `POST /login`. |
| `401 Unauthorized` | `{"code": 401, "message": "Refresh token non fornito"}` | Omissione del parametro obbligatorio `refresh_token` in notazione snake_case. |
| `403 Forbidden` | `{"code": 403, "message": "Access Denied"}` | Profilo privo dei privilegi di accesso per lo specifico alunno o risorsa. |
| `404 Not Found` | `{"code": 404, "message": "Not Found"}` | Percorso URI inesistente o risorsa non identificata. |
| `500 Internal Error` | `{"code": 500, "message": "..."}` | Eccezione interna al backend (frequente in caso di data non conforme al formato `DD-MM-YYYY`). |
