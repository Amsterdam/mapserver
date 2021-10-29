#!/bin/bash

# -----------------------------------------
# Purpose:
# -----------------------------------------
# 1. Place the TIF files in the source directory
# 2. Create pyramids in the destination directory using this script
# 3. Upload pyramid results to blob storage
# 4. Add lufoYYYY.map file
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
# ./lufopyramids.sh <source dir of tiffs> <destination dir of result> <YYYY> <infrarood | luchtfotos>
# ./lufopyramids.sh /mnt/lufo/2004 /mnt/lufo 2004 luchtfotos
# OR
# ./lufopyramids.sh /mnt/infrarood2018 /mnt/infrarood 2018 infrarood
# -----------------------------------------
#

### Set local vars
SOURCEDIR=$1
DESTDIR_ROOT=$2
DESTDIR=$2/pyramid
YEAR=$3
TYPE=$4

### Reset all tifs to use 3 bands:
# for i in $SOURCEDIR/*.tif; do
#     [ -f "$i" ] || break
#     gdal_translate $i $DESTDIR_ROOT/$(basename $i) -a_srs "EPSG:28992" -b 1 -b 2 -b 3
# done

# ### Create a list of images in the source directory
gdalbuildvrt -overwrite -resolution highest -r cubic -hidenodata -srcnodata "255 255 255" $DESTDIR_ROOT/overview.vrt $DESTDIR_ROOT/*.tif

### Clean up
if [ -d $DESTDIR ] ; then
   rm -rf $DESTDIR
fi

### Create pyramid base dir and retile to create pyramid with 5 levels in fixed tile sizes
mkdir -p $DESTDIR/0
gdal_retile.py -v -r cubic -levels 5 -resume -ps 8192 8192 -co TILED=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -s_srs "EPSG:28992" -targetDir $DESTDIR $DESTDIR_ROOT/overview.vrt

# TODO: Add gdal translate to add -co PHOTOMETRIC=YCBCR also for level 0

### Put original resolution images in their own subdirectory
mv $DESTDIR/*.tif $DESTDIR/0

### Set Levels and loop over them
### This exists to ensure public WMS usage is much quicker as the TIF files are in the blob storage
LEVELS=$(find $DESTDIR/* -type d -exec basename {} \; | sort)
for i in $LEVELS; do

### Create overviews to show when zoomed out of original resolution
    for j in $DESTDIR/$i/*.tif; do
        gdaladdo -r cubic --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL $j 2 4 8 16 32 64 128
    done

### Create tile indices for Mapserver WMS usage
    gdaltindex $DESTDIR/imagery-$YEAR-$i.shp $DESTDIR/$i/*.tif
    ogrinfo -dialect SQLITE -sql "UPDATE 'imagery-$YEAR-$i' SET location = '/vsicurl/https://files.data.amsterdam.nl/$TYPE/$YEAR/pyramid' || SUBSTR(location,length('$DESTDIR/'),length(location))" $DESTDIR/imagery-$YEAR-$i.shp
    ogrinfo -sql "CREATE SPATIAL INDEX ON imagery-$YEAR-$i" $DESTDIR/imagery-$YEAR-$i.shp

done

### Create tile index for Mapserver Tiling only
gdaltindex $DESTDIR_ROOT/imagery.shp $DESTDIR/0/*.tif

# # -----------------------------------------
# # Documentation:
# # -----------------------------------------
# #
# # http://www.gdal.org/frmt_gtiff.html
# # https://smathermather.wordpress.com/2016/05/01/efficient-delivery-of-raster-data-part-4/
# # https://smathermather.wordpress.com/2016/04/15/whichever-tiler-you-use-and-efficient-delivery-of-raster-data-image-pyramid-layer-update2/
# # https://astuntech.atlassian.net/wiki/display/ISHAREHELP/Mosaic+thousands+of+raster+images
# # http://blog.cleverelephant.ca/2015/02/geotiff-compression-for-dummies.html
# # https://www.slidesearch.net/slide/geoserver-in-production-we-do-it-here-is-how-foss4g-2016
# # https://www.mapbox.com/blog/super-sharp-pleiades-imagery-on-mapbox/
# # https://github.com/boundlessgeo/workshops/blob/master/workshops/data_configs/sphinx/source/raster.rst
# # http://www.ianturton.com/tutorials/bluemarble.html
# #
# # -----------------------------------------
