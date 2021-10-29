#!/bin/bash

# -----------------------------------------
# Purpose:
# -----------------------------------------
# 1. Use the level 0 JPEGs as source
# 2. Warp the JPEGs from RD to WM
# 5. Enable lufo layer in lufo.map file
# 6. Run mapproxy Lufo tiles generation (see mapproxy config)
# 7. Upload tiles to blob storage
#
# Requirements:
# -----------------------------------------
# sudo apt-get install -y gdal-bin python-gdal
#
# -----------------------------------------
# Usage:
# -----------------------------------------

# ./rd2wm.sh <source dir of tiffs>

## Set local vars
DESTDIR=/mnt/lufo
TILESDIR=/mnt/tiles
YEAR=$1

### Create tile index for Mapserver Tiling only
echo "Create Tileindex"
gdaltindex $DESTDIR/imagery.shp $DESTDIR/$YEAR/pyramid/0/*.tif

echo "Run Mapserver backend"
cd ~/code/mapserver
docker-compose up -d --build --force-recreate map

echo "Run Mapproxy Tiling"
cd ~/code/mapproxy
docker-compose run --rm topo-lufo-wm

echo "Cleanup"
rm $DESTDIR/imagery.*

# sudo mv $TILESDIR/lufo_wm_cache_EPSG3857 $TILESDIR/lufo${YEAR}_wm_cache_EPSG3857

# Rclone
# rclone copy lufo${YEAR}_wm_cache_EPSG3857 lufo:lufo${YEAR}_wm_cache_EPSG3857 -P --transfers=40 --checkers=40
# rclone copy lufo2003_wm_cache_EPSG3857 lufo:/lufo2003_wm_cache_EPSG3857 -P --transfers=40 --checkers=40
