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

echo Creating configuration files

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

# Configure apache to redirect errors to stderr.
# The mapserver will redirect errors to apache errorstream (see header.inc and private/header.inc)
# and apache will then redirect this to stderr, which will then be redirected to syslog/kibana.
# ref: http://mapserver.org/optimization/debugging.html#steps-to-enable-mapserver-debugging
#      https://serverfault.com/questions/711168/writing-apache2-logs-to-stdout-stderr
sed -i 's/ErrorLog .*/ErrorLog \/dev\/stderr/' /etc/apache2/apache2.conf
sed -i 's/Timeout 300/Timeout 600/' /etc/apache2/apache2.conf
# set listen port to non-privileged port
sed -i '0,/Listen [0-9]*/s//Listen 8080/' /etc/apache2/ports.conf
sed -i s/\<VirtualHost.*/\<VirtualHost\ \*\:8080\>/ /etc/apache2/sites-enabled/000-default.conf

# Replace actual location of the mapserver depending on the environment   
shopt -s globstar nullglob

for i in **/*.map; do
    sed -i 's#MAP_URL_REPLACE#'"$MAP_URL"'#g' $i
    sed -i 's#LEGEND_URL_REPLACE#'"$LEGEND_URL"'#g' $i
done

mkdir -p /srv/mapserver/config
# python3 /srv/mapserver/tools/make_mapfile_config.py > /srv/mapserver/sld/config.json

echo Make JSON index of maps
python3 /srv/mapserver/tools/make_indexjson.py /srv/mapserver/*.map > /srv/mapserver/index.json

echo Starting server
# Apache gets grumpy about PID files pre-existing
rm -f /var/run/apache2/apache2.pid

apachectl -D FOREGROUND
