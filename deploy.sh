#!/bin/bash

set -euo pipefail
# -e and -o pipefail will make the script exit
#    in case of command failure (or piped command failure)
# -u will exit in case a variable is undefined
#    (in you case, if the header is invalid)

echo
# echo '1. COPYING LATEST DATASET AND SCRIPTS'
# echo
# cp -r ../data .
# cp test.env .env

if [[ -e ".env" ]]
  then
    # loading script parameters from .env
    set -a            
    source .env
    set +a
else
    echo "No .env file with key paramaters found. Exiting."
    exit 1
fi

echo
echo '2. BUILDING DOCKER IMAGE...'
echo
docker compose build streamlit

sleep 5

echo
echo '3. RUNNING DOCKER COMPOSE... streamlit app will be available on port 8501'
echo
docker compose up &
