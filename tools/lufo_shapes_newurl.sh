#!/bin/bash

# -----------------------------------------
# Purpose:
# -----------------------------------------
# 1. Update shapefiles for new url
#
# -----------------------------------------
# Usage:
# -----------------------------------------
# ./lufo_shapes_newurl
#
# -----------------------------------------
# Requirements:
# -----------------------------------------
# sudo apt-get install -y gdal-bin python-gdal
#
# -----------------------------------------

set -u # crash on missing env
set -e # stop on any error
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#It's looking for the shapefiles in this folder, there in the main mapserver folder, you can move this file or move the shp files into this folder
SHAPEDIR=$SCRIPTDIR/luchtfoto
LEVELS="0 1 2 3 4 5"
YEAR="2024"

for j in $YEAR; do
    for i in $LEVELS; do
        # Extract only the filename after the last '/' and prepend new URL
        ogrinfo -dialect SQLITE -sql "
            UPDATE 'imagery-$j-$i' 
            SET location = '/vsicurl/https://basemaptilingappdatapi.blob.core.windows.net/tiles/luchtfoto/$j/pyramid/$i/' ||
                           substr(location, instr(location, 'overview'))
        " $SHAPEDIR/imagery-$j-$i.shp
        ogrinfo -sql "CREATE SPATIAL INDEX ON imagery-$j-$i" $SHAPEDIR/imagery-$j-$i.shp
    done
done




# SHAPEDIR=$SCRIPTDIR/infrarood
# LEVELS="0 1 2 3 4 5"
# YEAR="2018"

# for j in $YEAR; do
#     for i in $LEVELS; do
#         ogrinfo -dialect SQLITE -sql "UPDATE 'imagery-$j-$i' SET location = '/vsicurl/https://stlandingdpgoontweu01.blob.core.windows.net.' || SUBSTR(location, 18)" $SHAPEDIR/imagery-$j-$i.shp
#         ogrinfo -sql "CREATE SPATIAL INDEX ON imagery-$j-$i" $SHAPEDIR/imagery-$j-$i.shp
#     done
# done
