#!/usr/bin/env bash

set -e
set -u

BAG_V11_DB_PORT=${BAG_V11_DB_PORT:-5432}
BAG_V11_DB_NAME=${BAG_V11_DB_NAME:-bag_v11}
BAG_V11_DB_USER=${BAG_V11_DB_USER:-${BAG_V11_DB_NAME}}

NAP_DB_PORT=${NAP_DB_PORT:-5432}
NAP_DB_NAME=${NAP_DB_NAME:-nap}
NAP_DB_USER=${NAP_DB_USER:-${NAP_DB_NAME}}

MILIEUTHEMAS_DB_PORT=${MILIEUTHEMAS_DB_PORT:-5432}
MILIEUTHEMAS_DB_NAME=${MILIEUTHEMAS_DB_NAME:-milieuthemas}
MILIEUTHEMAS_DB_USER=${MILIEUTHEMAS_DB_USER:-${MILIEUTHEMAS_DB_NAME}}

PANORAMA_DB_PORT=${PANORAMA_DB_PORT:-5432}
PANORAMA_DB_NAME=${PANORAMA_DB_NAME:-panorama}
PANORAMA_DB_USER=${PANORAMA_DB_USER:-${PANORAMA_DB_NAME}}

BASISKAART_DB_PORT=${BASISKAART_DB_PORT:-5432}
BASISKAART_DB_NAME=${BASISKAART_DB_NAME:-basiskaart}
BASISKAART_DB_USER=${BASISKAART_DB_USER:-${BASISKAART_DB_NAME}}

HANDELSREGISTER_DB_PORT=${HANDELSREGISTER_DB_PORT:-5432}
HANDELSREGISTER_DB_NAME=${HANDELSREGISTER_DB_NAME:-handelsregister}
HANDELSREGISTER_DB_USER=${HANDELSREGISTER_DB_USER:-${HANDELSREGISTER_DB_NAME}}

MONUMENTEN_DB_PORT=${MONUMENTEN_DB_PORT:-5432}
MONUMENTEN_DB_NAME=${MONUMENTEN_DB_NAME:-monumenten}
MONUMENTEN_DB_USER=${MONUMENTEN_DB_USER:-${MONUMENTEN_DB_NAME}}

DATASELECTIE_DB_PORT=${DATASELECTIE_DB_PORT:-5432}
DATASELECTIE_DB_NAME=${DATASELECTIE_DB_NAME:-dataselectie}
DATASELECTIE_DB_USER=${DATASELECTIE_DB_USER:-${DATASELECTIE_DB_NAME}}

VARIOUS_SMALL_DATASETS_DB_PORT=${VARIOUS_SMALL_DATASETS_DB_PORT:-5432}
VARIOUS_SMALL_DATASETS_DB_NAME=${VARIOUS_SMALL_DATASETS_DB_NAME:-various_small_datasets}
VARIOUS_SMALL_DATASETS_DB_USER=${VARIOUS_SMALL_DATASETS_DB_USER:-${VARIOUS_SMALL_DATASETS_DB_NAME}}

DATASERVICES_DB_PORT=${DATASERVICES_DB_PORT:-5432}
DATASERVICES_DB_NAME=${DATASERVICES_DB_NAME:-dataservices}
DATASERVICES_DB_USER=${DATASERVICES_DB_USER:-${DATASERVICES_DB_NAME}}

echo Creating configuration files

cat > /srv/mapserver/connection_bag.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${BAG_V11_DB_HOST} dbname=${BAG_V11_DB_NAME} user=${BAG_V11_DB_USER} password=$(cat /mnt/secrets-store/bag-v11-db-password) port=${BAG_V11_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_nap.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${NAP_DB_HOST} dbname=${NAP_DB_NAME} user=${NAP_DB_USER} password=${/mnt/secrets-store/nap-db-password} port=${NAP_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_milieu.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${MILIEUTHEMAS_DB_HOST} dbname=${MILIEUTHEMAS_DB_NAME} user=${MILIEUTHEMAS_DB_USER} password=$(cat /mnt/secrets-store/milieuthemas-db-password) port=${MILIEUTHEMAS_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_panorama.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${PANORAMA_DB_HOST} dbname=${PANORAMA_DB_NAME} user=${PANORAMA_DB_USER} password=$(cat /mnt/secrets-store/panorama-db-password) port=${PANORAMA_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_monumenten.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${MONUMENTEN_DB_HOST} dbname=${MONUMENTEN_DB_NAME} user=${MONUMENTEN_DB_USER} password=$(cat /mnt/secrets-store/monumenten-db-password) port=${MONUMENTEN_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_basiskaart.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${BASISKAART_DB_HOST} dbname=${BASISKAART_DB_NAME} user=${BASISKAART_DB_USER} password=$(cat /mnt/secrets-store/basiskaart-db-password) port=${BASISKAART_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_handelsregister.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${HANDELSREGISTER_DB_HOST} dbname=${HANDELSREGISTER_DB_NAME} user=${HANDELSREGISTER_DB_USER} password=$(cat /mnt/secrets-store/handelsregister-db-password) port=${HANDELSREGISTER_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_dataselectie.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${DATASELECTIE_DB_HOST} dbname=${DATASELECTIE_DB_NAME} user=${DATASELECTIE_DB_USER} password=$(cat /mnt/secrets-store/dataselectie-db-password) port=${DATASELECTIE_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_various_small_datasets.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${VARIOUS_SMALL_DATASETS_DB_HOST} dbname=${VARIOUS_SMALL_DATASETS_DB_NAME} user=${VARIOUS_SMALL_DATASETS_DB_USER} password=$(cat /mnt/secrets-store/various-small-datasets-db-password) port=${VARIOUS_SMALL_DATASETS_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

cat > /srv/mapserver/connection_dataservices.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${DATASERVICES_DB_HOST} dbname=${DATASERVICES_DB_NAME} user=${DATASERVICES_DB_USER} password=$(cat /mnt/secrets-store/mdbdataservices-read) port=${DATASERVICES_DB_PORT}"
PROCESSING "CLOSE_CONNECTION=DEFER"
EOF

# Configure apache to redirect errors to stderr.
# The mapserver will redirect errors to apache errorstream (see header.inc and private/header.inc)
# and apache will then redirect this to stderr, which will then be redirected to syslog/kibana.
# ref: http://mapserver.org/optimization/debugging.html#steps-to-enable-mapserver-debugging
#      https://serverfault.com/questions/711168/writing-apache2-logs-to-stdout-stderr
sed -i 's/ErrorLog .*/ErrorLog \/dev\/stderr/' /etc/apache2/apache2.conf
sed -i 's/Timeout 300/Timeout 600/' /etc/apache2/apache2.conf

mkdir -p /srv/mapserver/config
python3 /srv/mapserver/tools/make_mapfile_config.py > /srv/mapserver/sld/config.json

echo Starting server
# Apache gets grumpy about PID files pre-existing
rm -f /var/run/apache2/apache2.pid
apachectl -D FOREGROUND
