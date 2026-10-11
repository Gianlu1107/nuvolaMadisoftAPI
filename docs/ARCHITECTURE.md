# Architettura di Rete e Considerazioni Tecniche di Nuvola

Il presente documento definisce la struttura architetturale dell'infrastruttura applicativa di Nuvola (Madisoft S.p.A.), le modalita di instradamento multi-tenant e le linee guida per la resilienza e l'interoperabilita del client.

---

## 1. Topologia dell'Infrastruttura di Backend

Dall'analisi delle risposte HTTP e dei certificati TLS/SSL, la topologia di servizio di Madisoft si articola come segue:

- **Perimetro di Bordo (Edge Network):** AWS CloudFront funge da reverse proxy globale, gestendo la terminazione crittografica TLS, la protezione contro attacchi DDoS volumetrici e l'applicazione delle regole WAF (Web Application Firewall).
- **Web Server Layer:** NGINX configurato con supporto HTTP/2 per la terminazione e l'instradamento verso i runtime applicativi.
- **Application Server Runtime:** Stack basato su PHP e framework Symfony.
- **Modello di Sharding Multi-Tenant:**  
  Madisoft serve centinaia di istituti scolastici italiani attraverso un'architettura multi-tenant federata. L'isolamento logico dei dati tra i singoli istituti non avviene tramite sottodomini dedicati, ma tramite **partizionamento a livello di base di dati guidato dal codice meccanografico ministeriale** dell'istituto (es. `RMIC8AB001`). Tale codice viene codificato nel claim `shard` del JWT e utilizzato dal layer ORM per instradare le query verso il cluster di database dedicato alla scuola corrispondente.

---

## 2. Analisi del Modello di Risposta a Involucro (Envelope Pattern)

A differenza dei pattern RESTful tradizionali che restituiscono direttamente un payload scalare o un vettore anonimo, Nuvola adotta un involucro JSON normalizzato:

```json
{
  "listeValori": null,
  "opzioni": [
    {
      "opzione": "assenza_mostra_turno",
      "impostazione": true
    }
  ],
  "valori": [ ... ],
  "paginatore": null
}
```

### Componenti dell'Involucro:
1. **`valori`**:  
   Contiene il nucleo informativo della risorsa richiesta. A seconda dell'endpoint, puo corrispondere a una lista ordinata di record (es. registro voti o compiti) o a un dizionario di attributi scalari (es. riepilogo notifiche).
2. **`opzioni`**:  
   Dizionario delle impostazioni di visibilita e autorizzazione stabilite dal dirigente scolastico o dall'amministratore del sistema per il modulo interrogato:
   - `assenza_mostra_turno`: Regola la visibilita della scansione per turni (mattutino/pomeridiano).
   - `assenze_abilita_giustificazioni`: Definisce se il tutore e abilitato a inserire giustificazioni telematiche.
   - `compito_mostra_argomento_lezione`: Stabilisce se associare formalmente il compito all'argomento didattico svolto in classe.
3. **`listeValori`**:  
   Mappe associative di decodifica (lookup tables) fornite direttamente nella risposta per evitare chiamate HTTP ridondanti (es. dizionario di conversione `classeId -> denominazioneClasse`).
4. **`paginatore`**:  
   Struttura predisposta per la paginazione basata su offset o cursore. Nelle interrogazioni su base temporale (giornaliera o per periodo didattico), il server valorizza convenzionalmente tale attributo a `null`.

---

## 3. Politica di Rispetto delle Risorse di Rete (Rate Limiting e Resilienza)

L'interfaccia esposta da Nuvola e un servizio critico erogato a supporto della didattica e dell'amministrazione scolastica nazionale. Ogni client automatico deve attenersi a criteri di efficienza:

1. **Frequenza di Consultazione Ragionata:**  
   Non eseguire interrogazioni cicliche ad alta frequenza (polling sub-minutario). I dati del registro elettronico possiedono una frequenza di aggiornamento intrinsecamente bassa:
   - Registro compiti: intervallo consigliato di 60-120 minuti.
   - Registro valutazioni: intervallo consigliato di 30-60 minuti durante le ore diurne.
   - Orario e argomenti: 1 interrogazione giornaliera mattutina.
2. **Riutilizzo del Token e Persistenza:**  
   Persistere sempre lo stato di autenticazione (`token`, `refreshToken`, `expires_at`). L'invocazione di `POST /refresh-token` richiede un dispendio computazionale trascurabile rispetto alla validazione completa delle credenziali tramite `POST /login`.
3. **Backoff Esponenziale:**  
   In presenza di codici di stato `HTTP 429 Too Many Requests` o errori transitori `HTTP 5xx`, il client deve implementare un algoritmo di backoff esponenziale con jitter per evitare la congestione della rete:
   $$T_{\text{wait}} = 2^k + \text{uniform}(0, 1)$$
4. **Intestazione User-Agent Coerente:**  
   Trasmettere un User-Agent conforme (`okhttp/4.9.2`) per prevenire falsi positivi nel sistema di analisi euristica del WAF di CloudFront.
