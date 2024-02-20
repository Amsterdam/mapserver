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

SHAPEDIR=$SCRIPTDIR/luchtfoto
LEVELS="0 1 2 3 4 5"
YEAR="2018 2017 2016 2015 2014 2013 2012 2011 2010 2009 2008 2007 2006 2005 2004 2003"

for j in $YEAR; do
    for i in $LEVELS; do
        ogrinfo -dialect SQLITE -sql "UPDATE 'imagery-$j-$i' SET location = '/vsicurl/https://files.' || SUBSTR(location, 18)" $SHAPEDIR/imagery-$j-$i.shp
        ogrinfo -sql "CREATE SPATIAL INDEX ON imagery-$j-$i" $SHAPEDIR/imagery-$j-$i.shp
    done
done

SHAPEDIR=$SCRIPTDIR/infrarood
LEVELS="0 1 2 3 4 5"
YEAR="2018"

for j in $YEAR; do
    for i in $LEVELS; do
        ogrinfo -dialect SQLITE -sql "UPDATE 'imagery-$j-$i' SET location = '/vsicurl/https://files.' || SUBSTR(location, 18)" $SHAPEDIR/imagery-$j-$i.shp
        ogrinfo -sql "CREATE SPATIAL INDEX ON imagery-$j-$i" $SHAPEDIR/imagery-$j-$i.shp
    done
done
