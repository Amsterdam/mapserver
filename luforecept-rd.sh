#!/bin/bash

# aanroepen voorbeeld:
# 
# ./luforecept-rd.sh <source dir of tiffs> <destination dir of result>
#
# Dit script wordt gedaan op een directory waarbinnen in de subdir “tiffsrc” de ruwe GeoTIFF bestanden staan.
# Het resultaat wordt geplaatst in de subdir “tiffdst” die moet bestaan.
# de bestanden uit
# /media/externaldrive/lufo/2015/tiffsrc <source dir of tiffs> bewerkt en geplaatst in
# /srv/mapserver/lufo/2015/ <destination dir of result>.

DIR=$1
cd $DIR

SRC_TIFF_FILES=`/bin/ls *.tif`
for SRC_TIFF_FILE in $SRC_TIFF_FILES; do
    echo "START $SRC_TIFF_FILE"
    # basis file naam
    BASE_NAME=`echo $SRC_TIFF_FILE | cut -d/ -f2 | cut -d'.' -f1`
    DEST_TIFF_FILE=$2/${BASE_NAME}.tif
    /bin/rm -f $DEST_TIFF_FILE

    echo "gdal_translate $SRC_TIFF_FILE $DEST_TIFF_FILE"

    # De eerste stap comprimeert vaak tot minder dan 10% van de oorspronkelijk omvang en maakt interne tiles aan.

    gdal_translate -co TILED=YES -a_srs "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.999908 +x_0=155000 +y_0=463000 +ellps=bessel +units=m +towgs84=565.2369,50.0087,465.658,-0.406857330322398,0.350732676542563,-1.8703473836068,4.0812 +no_defs no_defs" -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR $SRC_TIFF_FILE $DEST_TIFF_FILE

    # De tweede creëert gegeneraliseerde niveaus voor als je ver uitzoomt.

    echo "gdaladdo -$DEST_TIFF_FILE"

    gdaladdo -ro -r gauss --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR $DEST_TIFF_FILE 2 4 8 16 32 64 128

    echo "END $BASE_NAME"
done

# GeoTIFF-directory is oorspronkelijk 121G. Na conversie met GDAL blijft hier 7G van over!

# Maak een Esri Shape-bestand als index op de definitieve locatie van de GeoTIFFs.

# Plaats Esri shape-bestand bij de lufo's in de map
# Paden in de toekomst snel wijzigen?
# - converteer Esri Shape-bestand naar GeoJSON
# - pas paden in het GeoJSON-bestand aan mbv texteditor
# - converteer GeoJSON-bestand terug naar Esri Shape-bestand
#
# Maak een MapServer configuratie aan:
# 
# LAYER
#  NAME "lufo2015"
#  TILEINDEX "/srv/mapserver/lufo/2015/imagery.shp"
#  TILEITEM "location"
#  TYPE RASTER
# END

# MapProxy configuratie as usual.. verwijzen naar de juiste WMS endpoint
# Wel opslaan als JPG-bestanden: veel kleiner en mooier voor lufo's dan PNG-bestanden


#Steps to introduce a new year:
#- Copy original full size tiff to laptop
#- Run above script
#- Upload resulting tiffs to objectstore
#- Add settings to mapserver, mapproxy, objectstore
#- Run script below
#
#    #ls 2016/ | grep -e "\.tif$" | awk '{print "/vsicurl/https://atlas.amsterdam.nl/luchtfotos/2016/"$1}' | xargs gdaltindex 2016-imagery.shp
#
#- Run tiling script on jenkins
#- Upload tiles to objectstore
#- Update frontend
