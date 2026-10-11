# Politica di Sicurezza

## Divulgazione Responsabile (Responsible Disclosure)

Se identifichi una vulnerabilità di sicurezza all'interno del codice di questa libreria o riscontri comportamenti critici:

1. **Non aprire una issue pubblica su GitHub.**
2. Invia una segnalazione riservata all'autore / maintainer del progetto o apri un Security Advisory privato su GitHub.
3. Se riscontri una vulnerabilità che riguarda direttamente l'infrastruttura backend di Madisoft S.p.A., ti invitiamo a contattare tempestivamente il team di sicurezza di Madisoft attraverso i loro canali ufficiali di contatto (pec / supporto tecnico istituzionale).

## Protezione delle Credenziali Locali

- Il file `nuvola_session.json` contiene token crittografici che garantiscono l'accesso al registro elettronico dello studente.
- Assicurati che tale file rimanga escluso dal controllo versione (`.gitignore`) e che i permessi del file system siano restrittivi (`chmod 600 nuvola_session.json`).
