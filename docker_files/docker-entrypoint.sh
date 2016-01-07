#!/usr/bin/env bash

set -e
set -u

echo Starting server
/bin/bash -c "source /etc/apache2/envvars && exec /usr/sbin/apache2 -DFOREGROUND"
