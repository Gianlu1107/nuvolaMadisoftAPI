# Specifiche Tecniche di Autenticazione e Gestione della Sessione

Il presente documento definisce nel dettaglio i protocolli di sicurezza, i meccanismi crittografici e le procedure operative adottate dalla piattaforma Nuvola (Madisoft S.p.A.) per la gestione delle identita e delle sessioni applicative.

---

## 1. Architettura dei Canali di Accesso

La piattaforma Nuvola espone due differenti modalita di autenticazione:

```
[Client / Utente]
   |
   +--- (1) Canale Mobile REST Nativo ----------> POST /api-studente/v1/login (Accesso Diretto)
   |                                               |-- Emissione Bearer JWT (1800s) + Refresh Token
   |
   +--- (2) Canale Portale Web (OIDC) ----------> Keycloak (auth.nuvola.madisoft.it)
                                                   |-- Vincolo obbligatorio SPID/CIE per gli istituti configurati
```

### 1.1 Disaccoppiamento dal Vincolo SPID/CIE nel Flusso Mobile
Numerosi istituti scolastici italiani hanno disposto l'accesso esclusivo al portale web tramite identita digitale (SPID livello 2 o CIE), disabilitando i form di autenticazione standard basati su username e password via browser.

L'applicazione mobile ufficiale distribuita per sistemi Android e iOS (*it.madisoft.areatutorestudente*) implementa un'interfaccia di comunicazione diretta verso l'endpoint REST `/api-studente/v1/login`. Tale endpoint:
- Accetta le credenziali alfanumeriche primarie assegnate dalla segreteria scolastica.
- Non richiede l'intermediazione del gateway federato SPID/CIE.
- Rilascia una coppia di token crittografici (JWT e Refresh Token) per la gestione autonoma della persistenza.

---

## 2. Struttura Crittografica del JSON Web Token (JWT)

Il token di accesso rilasciato all'atto del login e conforme allo standard RFC 7519 ed e firmato digitalmente tramite algoritmo asimmetrico ad alta sicurezza **RS256** (RSA Signature con digest SHA-256).

### 2.1 Intestazione (Header)
```json
{
  "typ": "JWT",
  "alg": "RS256"
}
```

### 2.2 Carico Utile (Payload Decodificato)
```json
{
  "iat": 1791745710,
  "exp": 1791747510,
  "iss": "nuvola",
  "uuid": "d4e5f6a7-b8c9-4012-a345-6789abcdef01",
  "shard": "RMIC8AB001",
  "applicazione": "APP",
  "anagrafica_id": "1042"
}
```

### 2.3 Analisi dei Claim Registrati e Personalizzati
- `iat` (Issued At): Timestamp Unix corrispondente all'istante di generazione del token.
- `exp` (Expiration Time): Timestamp Unix di scadenza. La finestra di validita e rigidamente fissata a **1800 secondi (30 minuti esatti)**:
  $$\Delta t = \text{exp} - \text{iat} = 1800\text{ s}$$
- `iss` (Issuer): Entita emittente accreditata, convenzionalmente valorizzata come `"nuvola"`.
- `uuid`: Identificativo univoco globale (UUID v4) associato all'utenza nel database centrale dei servizi Madisoft.
- `shard`: **Codice meccanografico ministeriale dell'istituto scolastico** (es. `RMIC8AB001`). Tale parametro e utilizzato dal layer di instradamento del backend per selezionare il database dedicato dell'istituto nel contesto dell'architettura multi-tenant federata.
- `applicazione`: Tipologia di applicazione mittente (`"APP"` per client mobili nativi, `"WEB"` per sessioni generate da browser).
- `anagrafica_id`: Chiave primaria numerica del soggetto nel database locale della scuola.

---

## 3. Gestione del Ciclo di Vita del Token e Rinnovo Automatico

Al superamento dei 1800 secondi di validita, il server respinge qualsiasi richiesta protetta con stato `HTTP 401 Unauthorized`.  
Per garantire la continuita del servizio senza memorizzare in chiaro le credenziali dell'utente in memoria volatile o su disco, la procedura prevede l'utilizzo del `refreshToken`.

```
                        +-------------------------------+
                        |  POST /api-studente/v1/login  |
                        +---------------+---------------+
                                        | (200 OK)
                                        v
                          Ricezione JWT + refreshToken
                                        |
                    +-------------------+-------------------+
                    |                                       |
                    v                                       v
         Fase Operativa (0-28 min)             Finestra di Rinnovo (>= 28 min)
                    |                                       |
                    v                                       v
          Chiamate ordinarie                  POST /api-studente/v1/refresh-token
       (Authorization: Bearer JWT)             Body: {"refresh_token": "..."}
                                                            | (200 OK)
                                                            v
                                                Emissione nuovo JWT e rotazione
```

### 3.1 Dettaglio di Implementazione: Convenzione dei Nomi (CamelCase vs snake_case)
L'integrazione richiede rigorosa attenzione alla forma dei campi JSON nei due flussi:

1. **Nella risposta del server (`POST /login`):**
   La chiave contenente il token di rinnovo e formattata in camelCase:
   ```json
   {
     "token": "...",
     "refreshToken": "7a8b9c0d1e2f3a4b..."
   }
   ```

2. **Nella richiesta di rinnovo al server (`POST /refresh-token`):**
   La chiave nel corpo JSON deve essere tassativamente in snake_case:
   ```json
   {
     "refresh_token": "7a8b9c0d1e2f3a4b..."
   }
   ```
   L'invio errato del campo come `refreshToken` causa un errore di validazione `HTTP 401 Unauthorized` con il messaggio:
   `{"code": 401, "message": "Refresh token non fornito"}`.

---

## 4. Architettura di Caching e Persistenza Locale

Al fine di minimizzare il carico computazionale sui server e ottimizzare i tempi di risposta, il client implementa la persistenza controllata della sessione su un file JSON protetto (`nuvola_session.json`):

```json
{
  "token": "eyJhbGciOiJSUzI1NiIsIn...",
  "refreshToken": "7a8b9c0d1e2f3a4b5c6d...",
  "idAnagrafica": 1042,
  "codiceCliente": "RMIC8AB001",
  "expires_at": 1791747510.0
}
```

### Algoritmo di Risoluzione del Token
All'atto di ogni operazione di rete:
1. Viene calcolato il tempo rimanente: $\Delta = \text{expires\_at} - \text{now}()$.
2. Se $\Delta > 60$ secondi, il token memorizzato viene ritenuto pienamente valido e utilizzato senza chiamate preliminari.
3. Se $\Delta \le 60$ secondi ed e presente un `refreshToken`, viene invocato `POST /refresh-token`.
4. Nel caso in cui il refresh restituisca un errore (es. revoca del token lato server) e siano configurate credenziali d'accesso valide, viene eseguito il fallback su `POST /login`.
5. Se tutte le strategie automatiche falliscono, viene sollevata un'eccezione tipizzata `NuvolaAuthError`.

---

## 5. Canale Web Legacy (Keycloak / OIDC Session Cookie)

Qualora sia disponibile una sessione autenticata originata da browser Web:
1. L'utente esegue l'accesso su `https://nuvola.madisoft.it`.
2. Viene estratto dal cookie jar il valore del cookie di sessione `nuvola`.
3. Viene eseguita una chiamata di conversione:
   ```http
   GET /api-studente/v1/login-from-web HTTP/1.1
   Host: nuvola.madisoft.it
   Cookie: nuvola=<VALORE_COOKIE_SESSIONE>
   Accept: application/json
   ```
4. L'endpoint restituisce il Bearer Token JWT equivalente utilizzabile per le successive chiamate REST:
   ```json
   {
     "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```
