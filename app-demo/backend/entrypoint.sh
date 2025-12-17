#!/bin/sh
# Aspetta che il file localstack.env esista

ENV_FILE="/config/localstack.env"

while [ ! -f "$ENV_FILE" ]; do
  echo "Waiting for $ENV_FILE ..."
  sleep 10
done

# Esporta SOLO linee valide KEY=VALUE
# set -o allexport
# for line in $(grep -v '^#' "$ENV_FILE" | grep -v '^$'); do
#     eval "$line"
# done
# set +o allexport

# "set -a" esporta tutte le variabili caricate
# "." (source) esegue il file mantenendo gli spazi e i caratteri speciali corretti
set -a
. "$ENV_FILE"
set +a

# Debug: stampa tutte le variabili esportate
echo "Loaded environment variables:"
echo "=========================================="
env | sort
echo "=========================================="
# Avvia il comando originale del CMD
exec "$@"
