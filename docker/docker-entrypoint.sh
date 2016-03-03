#!/usr/bin/env bash

set -e
set -u

ATLAS_DB_HOST=${ATLAS_DB_PORT_5432_TCP_ADDR:-atlas_db.service.consul}
ATLAS_DB_PORT=${ATLAS_DB_PORT_5432_TCP_PORT:-5432}
ATLAS_DB_USER=${ATLAS_DB_USER:-${ATLAS_DB_NAME}}

NAP_DB_HOST=${NAP_DB_PORT_5432_TCP_ADDR:-nap_db.service.consul}
NAP_DB_PORT=${NAP_DB_PORT_5432_TCP_PORT:-5432}
NAP_DB_USER=${NAP_DB_USER:-${NAP_DB_NAME}}

MILIEU_DB_HOST=${MILIEU_DB_PORT_5432_TCP_ADDR:-milieu_db.service.consul}
MILIEU_DB_PORT=${MILIEU_DB_PORT_5432_TCP_PORT:-5432}
MILIEU_DB_USER=${MILIEU_DB_USER:-${MILIEU_DB_NAME}}

PANO_DB_HOST=${PANO_DB_PORT_5432_TCP_ADDR:-panorama_db.service.consul}
PANO_DB_PORT=${PANO_DB_PORT_5432_TCP_PORT:-5432}
PANO_DB_USER=${PANO_DB_USER:-${PANO_DB_NAME}}


echo Creating configuration files

cat > /srv/mapserver/connection.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${ATLAS_DB_HOST} dbname=${ATLAS_DB_NAME} user=${ATLAS_DB_USER} password=${ATLAS_DB_PASSWORD} port=${ATLAS_DB_PORT}"
EOF

cat > /srv/mapserver/connection_nap.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${NAP_DB_HOST} dbname=${NAP_DB_NAME} user=${NAP_DB_USER} password=${NAP_DB_PASSWORD} port=${NAP_DB_PORT}"
EOF

cat > /srv/mapserver/connection_milieu.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${MILIEU_DB_HOST} dbname=${MILIEU_DB_NAME} user=${MILIEU_DB_USER} password=${MILIEU_DB_PASSWORD} port=${MILIEU_DB_PORT}"
EOF

cat > /srv/mapserver/connection_panorama.inc <<EOF
CONNECTIONTYPE postgis
CONNECTION "host=${PANO_DB_HOST} dbname=${PANO_DB_NAME} user=${PANO_DB_USER} password=${PANO_DB_PASSWORD} port=${PANO_DB_PORT}"
EOF


echo Starting server
apachectl -D FOREGROUND
