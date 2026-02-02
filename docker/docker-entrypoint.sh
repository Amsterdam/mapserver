#!/usr/bin/env bash

set -e
set -u

PANORAMA_DB_PORT=${PANORAMA_DB_PORT:-5432}
PANORAMA_DB_NAME=${PANORAMA_DB_NAME:-panorama}
PANORAMA_DB_USER=${PANORAMA_DB_USER:-${PANORAMA_DB_NAME}}
PANORAMA_DB_PASSWORD_PATH=${PANORAMA_DB_PASSWORD_PATH:-'/mnt/secrets-store/mapserver-public'}

DATASERVICES_DB_PORT=${DATASERVICES_DB_PORT:-5432}
DATASERVICES_DB_NAME=${DATASERVICES_DB_NAME:-dataservices}
DATASERVICES_DB_USER=${DATASERVICES_DB_USER:-${DATASERVICES_DB_NAME}}
DATASERVICES_DB_PASSWORD_PATH=${DATASERVICES_DB_PASSWORD_PATH:-'/mnt/secrets-store/mapserver-public'}
LOCAL=${LOCAL:-false}

if [[ $LOCAL == "true" ]]
then
    echo 'Warning running in LOCAL development mode';
    echo ${PANORAMA_DB_PASSWORD} > /srv/mapserver/connection/panorama_pw;
    PANORAMA_DB_PASSWORD_PATH='/srv/mapserver/connection/panorama_pw';
    echo ${DATASERVICES_DB_PASSWORD} > /srv/mapserver/connection/dataservices_pw;
    DATASERVICES_DB_PASSWORD_PATH='/srv/mapserver/connection/dataservices_pw';
fi

echo Creating configuration files

mkdir -p /srv/mapserver/connection

cat > /srv/mapserver/connection/panorama.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${PANORAMA_DB_HOST} dbname=${PANORAMA_DB_NAME} user=${PANORAMA_DB_USER} password=$(cat ${PANORAMA_DB_PASSWORD_PATH}) port=${PANORAMA_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection/dataservices.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${DATASERVICES_DB_HOST} dbname=${DATASERVICES_DB_NAME} user=${DATASERVICES_DB_USER} password=$(cat ${DATASERVICES_DB_PASSWORD_PATH}) port=${DATASERVICES_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

# Replace actual location of the mapserver depending on the environment
shopt -s globstar nullglob

# python3 /srv/mapserver/tools/make_mapfile_config.py > /srv/mapserver/sld/config.json

echo Starting server
# Apache gets grumpy about PID files pre-existing
rm -f /var/run/apache2/apache2.pid

apachectl -D FOREGROUND
