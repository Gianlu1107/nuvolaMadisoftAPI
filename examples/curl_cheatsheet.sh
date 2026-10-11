#!/usr/bin/env bash
# ==============================================================================
# Nuvola API - Cheat-Sheet comandi cURL
# ==============================================================================
# Questo script contiene le chiamate cURL di riferimento per interrogare Nuvola.
# Sostituisci i valori segnaposto o esporta le variabili d'ambiente corrispondenti.
# ==============================================================================

BASE_URL="https://nuvola.madisoft.it/api-studente/v1"
USER_AGENT="okhttp/4.9.2"

# 1. Login iniziale (Bypass SPID/CIE)
echo "=== 1. Login ==="
curl -s -X POST "${BASE_URL}/login" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" \
  -d '{
    "username": "mario.rossi",
    "password": "PasswordFittizia123!"
  }' | jq .

# 2. Rinnovo Token (Refresh)
# NOTA: il body richiede la chiave snake_case "refresh_token"
echo -e "\n=== 2. Refresh Token ==="
curl -s -X POST "${BASE_URL}/refresh-token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" \
  -d '{
    "refresh_token": "TUO_REFRESH_TOKEN"
  }' | jq .

# 3. Elenco Alunni Associati
echo -e "\n=== 3. Elenco Alunni ==="
curl -s -X GET "${BASE_URL}/alunni" \
  -H "Authorization: Bearer TUO_BEARER_TOKEN" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" | jq .

# 4. Compiti per Data (DD-MM-YYYY)
echo -e "\n=== 4. Compiti per Data ==="
curl -s -X GET "${BASE_URL}/alunno/12345/compito/elenco/15-10-2026?contextAlunno=12345" \
  -H "Authorization: Bearer TUO_BEARER_TOKEN" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" | jq .

# 5. Orario e Argomenti Lezione del Giorno
echo -e "\n=== 5. Orario e Argomenti Lezione ==="
curl -s -X GET "${BASE_URL}/alunno/12345/argomento-lezione/elenco/15-10-2026?contextAlunno=12345" \
  -H "Authorization: Bearer TUO_BEARER_TOKEN" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" | jq .

# 6. Eventi e Verifiche di Classe
echo -e "\n=== 6. Eventi di Classe ==="
curl -s -X GET "${BASE_URL}/alunno/12345/eventi-classe?contextAlunno=12345" \
  -H "Authorization: Bearer TUO_BEARER_TOKEN" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" | jq .

# 7. Tutti i Voti dell'Alunno
echo -e "\n=== 7. Voti ==="
curl -s -X GET "${BASE_URL}/alunno/12345/voti?contextAlunno=12345" \
  -H "Authorization: Bearer TUO_BEARER_TOKEN" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" | jq .

# 8. Assenze e Ritardi
echo -e "\n=== 8. Assenze ==="
curl -s -X GET "${BASE_URL}/alunno/12345/assenze?contextAlunno=12345" \
  -H "Authorization: Bearer TUO_BEARER_TOKEN" \
  -H "Accept: application/json" \
  -H "User-Agent: ${USER_AGENT}" | jq .
