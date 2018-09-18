#!/bin/bash

# -----------------------------------------
# Purpose:
# -----------------------------------------
# 1. Take the files from the source directory
# 2. Create pyramids in the destination directory
# 3. Createtile indices
#
#
# -----------------------------------------
# Usage:
# -----------------------------------------
# ./lufopyramids.sh <source dir of tiffs> <destination dir of result> <YYYY>
# ./lufopyramids.sh /srv/lufo/2004 /srv/lufo 2004
#
# -----------------------------------------
# Requirements:
# -----------------------------------------
# sudo apt-get install -y gdal-bin python-gdal
#
# -----------------------------------------
#
# From 2018 the files need to be translated first. Run this in the dir of the external harddrive
#
# for i in *.tif; do
#     [ -f "$i" ] || break
#     gdal_translate $i /mnt/lufo2018/$i -b 1 -b 2 -b 3 -mask 4 --config GDAL_TIFF_INTERNAL_MASK YES
# done
#
# cp -a *.aux /mnt/lufo2018
# cp -a *.tfw /mnt/lufo2018

SOURCEDIR=$1
DESTDIR_ROOT=$2
DESTDIR=$2/pyramid
YEAR=$3

# Create a list of images in the source directory

if [ -f /tmp/list.txt ] ; then
    rm -r /tmp/list.txt
fi

ls $SOURCEDIR/*.tif > /tmp/list.txt

if [ -d $DESTDIR ] ; then
    rm -rf $DESTDIR
fi

mkdir -p $DESTDIR/0
gdal_retile.py -v -r cubic -levels 5 -ps 8192 8192 -co TILED=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -s_srs "EPSG:28992" -targetDir $DESTDIR --optfile /tmp/list.txt

# Put original resolution images in their own subdirectory

mv $DESTDIR/*.tif $DESTDIR/0
LEVELS=$(find $DESTDIR/* -type d -exec basename {} \; | sort)

for i in $LEVELS; do

# Create overviews to show when zoomed out of original resolution

    for j in $DESTDIR/$i/*.tif; do
        gdaladdo -r cubic --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL $j 2 4 8 16 32 64 128
    done

# Create tile indices

    gdaltindex $DESTDIR/imagery-$YEAR-$i.shp $DESTDIR/$i/*.tif

    ogrinfo -dialect SQLITE -sql "UPDATE 'imagery-$YEAR-$i' SET location = '/vsicurl/https://data.amsterdam.nl/luchtfotos/$YEAR/pyramid' || SUBSTR(location,length('$DESTDIR/'),length(location))" $DESTDIR/imagery-$YEAR-$i.shp

    ogrinfo -sql "CREATE SPATIAL INDEX ON imagery-$YEAR-$i" $DESTDIR/imagery-$YEAR-$i.shp

done

gdaltindex $DESTDIR_ROOT/imagery.shp $DESTDIR/0/*.tif

# -----------------------------------------
# Documentation:
# -----------------------------------------
#
# http://www.gdal.org/frmt_gtiff.html
# https://smathermather.wordpress.com/2016/05/01/efficient-delivery-of-raster-data-part-4/
# https://smathermather.wordpress.com/2016/04/15/whichever-tiler-you-use-and-efficient-delivery-of-raster-data-image-pyramid-layer-update2/
# https://astuntech.atlassian.net/wiki/display/ISHAREHELP/Mosaic+thousands+of+raster+images
# http://blog.cleverelephant.ca/2015/02/geotiff-compression-for-dummies.html
# https://www.slidesearch.net/slide/geoserver-in-production-we-do-it-here-is-how-foss4g-2016
# https://www.mapbox.com/blog/super-sharp-pleiades-imagery-on-mapbox/
# https://github.com/boundlessgeo/workshops/blob/master/workshops/data_configs/sphinx/source/raster.rst
# http://www.ianturton.com/tutorials/bluemarble.html
#
# -----------------------------------------
