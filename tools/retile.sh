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
# sudo apt install -y gdal-bin python-gdal rename
#
# -----------------------------------------
# Usage:
# -----------------------------------------

### ECW to TIFF
## Translate ECW to TIFF
# for i in *.ecw
# do
#   docker run --rm -it --name gdalecw -v /mnt/weesp/2005/ECW:/home/datafolder ginetto/gdal:2.4.4_ECW gdal_translate /home/datafolder/$i /home/datafolder/$i.tif
# done
#
## Make all near-white pixels white - to improve transparency
# for i in *.tif; do 
#   nearblack -white -of GTiff -o Z_$i $i
# done

## Set local vars
SOURCEDIR_ADAM=/mnt/luchtfotos
SOURCEDIR_WEESP=/mnt/weesp
DESTDIR=/mnt/lufo
TILESDIR=/mnt/tiles
YEAR=$1

mkdir -p $DESTDIR/$YEAR

## Reset all tifs to use 3 bands:
for i in $SOURCEDIR_ADAM/$YEAR/pyramid/0/*.tif; do     
    [ -f "$i" ] || break
    gdal_translate $i $DESTDIR/$YEAR/$(basename $i) -a_srs "EPSG:28992" -b 1 -b 2 -b 3
done

echo "Copy Amsterdam"
cp -a $SOURCEDIR_ADAM/$YEAR/pyramid/0/*.tif $DESTDIR/$YEAR/

cd $DESTDIR/$YEAR
echo "Rename Amsterdam"
rename 's/^/0_/' *.tif

# # # WEESP ONLY
echo "Translate Weesp Tiffs"
for i in $SOURCEDIR_WEESP/$YEAR/TIFF/*.tif; do
    [ -f "$i" ] || break
    gdal_translate $i $DESTDIR/$YEAR/$(basename $i) -a_srs "EPSG:28992" -b 1 -b 2 -b 3
done

echo "Build VRT file"
# ### Create a list of images in the source directory
gdalbuildvrt -overwrite -resolution highest -r cubic -hidenodata -srcnodata "255 255 255" $DESTDIR/$YEAR/overview.vrt $DESTDIR/$YEAR/*.tif

### Create base dir and retile in fixed tile sizes
mkdir -p $DESTDIR/$YEAR/0
echo "Retile level 0"
gdal_retile.py -v -r cubic -resume -ps 8192 8192 -co TILED=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -s_srs "EPSG:28992" -targetDir $DESTDIR/$YEAR/0 $DESTDIR/$YEAR/overview.vrt
