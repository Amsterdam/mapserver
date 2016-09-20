#!/bin/bash

# aanroepen voorbeeld:
# 
# ./luforecept-rd.sh <source dir of tiffs> <destination dir of result>
#
# Dit script wordt gedaan op de bestanden uit
# /media/externaldrive/lufo/2015/tiffsrc <source dir of tiffs> en plaatst deze in
# /srv/mapserver/lufo/2015/ <destination dir of result>.

DIR=$1
cd $DIR
YEAR=dir=$(basename $2)

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

# Now create composite as an overview image for small scale portrayal 

gdalwarp -r lanczos -tr 15 15 *.tif overview-$YEAR.tif

# Add external overviews too

gdaladdo -ro -r gauss --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR overview-$YEAR.tif 2 4 8 16 32 64 128

# Maak een Esri Shape-bestand als index op de definitieve locatie van de GeoTIFFs.

# Plaats Esri shape-bestand bij de lufo's in de map
# Paden in de toekomst snel wijzigen?
# - converteer Esri Shape-bestand naar GeoJSON
# - pas paden in het GeoJSON-bestand aan mbv texteditor
# - converteer GeoJSON-bestand terug naar Esri Shape-bestand
#

# Maak een MapServer configuratie aan:

# LAYER
#  NAME          "lufo2012-smallscale"
#  GROUP         "lufo2012"
#  DATA           "/vsicurl/https://atlas.amsterdam.nl/luchtfotos/2012/overview-2012.tif"
#  TYPE           RASTER
#  MAXSCALEDENOM  400000
#  MINSCALEDENOM  25000
# END
#
# LAYER
#  NAME           "lufo2012-largescale"
#  GROUP          "lufo2012
#  TILEINDEX      "/srv/mapserver/lufo/2012/imagery.shp"
#  TILEITEM       "location"
#  TYPE           RASTER
#  MAXSCALEDENOM  25000
# END

# Add Cascading WMS to existing Mapserver configuration:

# LAYER
#  NAME                    "lufo2012"
#  GROUP                   "lufo"
#  CONNECTION              "http://map.datapunt.amsterdam.nl/maps/lufo2012"
#  CONNECTIONTYPE          WMS
#  TYPE                    RASTER
#
#  METADATA
#    "wms_name"            "lufo2012"
#    "wms_format"          "image/tiff"
#    "wms_server_version"  "1.1.1"
#  END
# END

# MapProxy configuratie as usual.. verwijzen naar de juiste WMS endpoint
# Wel opslaan als JPG-bestanden: veel kleiner en mooier voor lufo's dan PNG-bestanden


# Steps to introduce a new year:
# Copy original full size tiff to laptop
# Run above script
# Upload resulting tiffs to objectstore
# Add settings to mapserver, mapproxy, objectstore
# Run script below (don't include the overview-YYYY.tif only after)
#
# ls 2016/ | grep -e "\.tif$" | awk '{print "/vsicurl/https://atlas.amsterdam.nl/luchtfotos/2016/"$1}' | xargs gdaltindex 2016-imagery.shp
#
# For local files:
# gdaltindex imagery.shp /srv/mapserver/lufo/2016/*.tif
#
# Then run Shptree to create a quadtree index of shape file:
# shptree 2016-imagery.shp
# 
#
# Run tiling script on jenkins
# Upload tiles to objectstore
# Update frontend

#CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif .ovr" gdalinfo /vsicurl/https://acc.atlas.amsterdam.nl/luchtfotos/2015/109850_481580.tif
