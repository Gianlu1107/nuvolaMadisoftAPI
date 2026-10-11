# Guida per la Contribuzione

Il presente documento definisce le linee guida tecniche ed etiche per i contributi al progetto Nuvola API.

---

## 1. Riservatezza dei Dati e Sanificazione

Trattandosi di documentazione e strumenti software per l'interazione con piattaforme scolastiche:

1. **Divieto di inserimento di dati personali reali:**
   - Nominativi di docenti, dirigenti scolastici o personale ATA.
   - Dati anagrafici, identificativi numerici e date di nascita di studenti o tutori legali.
   - Codici fiscali.
   - Codici meccanografici di istituti reali (utilizzare esclusivamente codici standard fittizi quali `RMIC8AB001`).
   - Token crittografici (JWT) o Refresh Token autentici e non scaduti.

2. **Dati dimostrativi:**
   Tutti gli esempi, test unitari e frammenti di codice inclusi nelle modifiche devono impiegare esclusivamente payload sintetici e sanificati.

---

## 2. Condotta Etica e Sicurezza Operativa

Il progetto persegue finalità di ricerca, studio architetturale, interoperabilità e automazione lecita:

- E' vietata qualsiasi forma di attacco denial-of-service, scansione aggressiva o flooding verso l'infrastruttura di rete di Madisoft S.p.A.
- E' rigorosamente vietato il tentativo di accesso non autorizzato a profili o archivi di dati appartenenti a soggetti terzi (ai sensi dell'art. 615-ter del Codice Penale).
- Ogni client o procedura automatica deve implementare un intervallo di consultazione prudenziale (rate limiting) per non alterare la normale operativita dei servizi scolastici.

---

## 3. Ambiente di Sviluppo e Standard di Codice

1. Clonare la repository ed accedere alla directory del progetto:
   ```bash
   git clone <URL_REPOSITORY>
   cd nuvolaMadisoftAPI
   ```

2. Esecuzione della suite di test unitari (nessuna dipendenza esterna richiesta):
   ```bash
   python3 -m unittest discover -s tests -v
   ```

3. Installazione in modalita editabile con gli strumenti di verifica statica:
   ```bash
   pip install -e ".[dev]"
   ```

4. Conformita stilistica:
   - Rispetto degli standard PEP 8.
   - Annotazioni di tipo statiche complete (verificate tramite `mypy`).
   - Assenza tassativa di emoji o simboli informali nel codice sorgente, nei log e nella documentazione.

---

## 4. Procedura di Sottomissione delle Modifiche

1. Aprire un Issue descrittivo per esporre la proposta di modifica o il nuovo endpoint individuato.
2. Creare un branch dedicato con nomenclatura convenzionale (es. `feature/supporto-circolari`).
3. Verificare che l'intera suite di test mantenga esito positivo e implementare i test a copertura del nuovo codice.
4. Sottomettere una Pull Request accompagnata da documentazione tecnica esaustiva.
