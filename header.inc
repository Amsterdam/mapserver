#==============================================================================
#
# header.map
# doel: algemene header-informatie dat voor alle map-bestanden gelijk is.
#
#==============================================================================



  #=============================================================================
  # MAP: debug
  #=============================================================================

  # CONFIG   "MS_ERRORFILE" "/srv/mapserver/ms_error.txt"

  # Redirect errors to apache errorstream
  # ENABLE for debugging purposes - quite spammy
  # CONFIG   "MS_ERRORFILE" stderr

  # DEBUG    5
  # For errors from underlying GDAL (shows SQL query issues) -- is spammy
  # CONFIG "CPL_DEBUG" "ON"
  # CONFIG "PROJ_DEBUG" "ON"



  #=============================================================================
  # MAP: algemeen
  #=============================================================================

  EXTENT      94000 465000 170000 514000
  UNITS       meters
  MAXSIZE     4000
  STATUS      ON

  # VPS06
  FONTSET     "fonts/fontlist.txt"
  SYMBOLSET   "symbols/symbollist.txt"
  # SHAPEPATH ""



  #=============================================================================
  # MAP: algemeen uitvoer
  #=============================================================================

  IMAGETYPE   png

  WEB
    METADATA
      "ows_enable_request"           "*"
      "ows_srs"                      "EPSG:28992 EPSG:4326 EPSG:3857 EPSG:4258"
      "ows_feature_info_mime_type"   "application/json"
      "wms_format"                   "image/png"

      "wfs_encoding"                 "UTF-8"
      "wfs_maxfeatures"              "500000"
      "wfs_getfeature_formatlist"    "gml,geojson,csv,shapezip,spatialzip"

      # verplicht om aan de OGC standaard te voldoen:
      "ows_contactorganization"      "gemeente Amsterdam"
      "ows_contactperson"            "Onderzoek, Informatie en Statistiek"
    END

    IMAGEPATH                        "/srv/mapserver/tmp_img/"
    IMAGEURL                         "/ms_tmp/"
    BROWSEFORMAT                     "image/svg+xml"

    VALIDATION
      "MAP_RESOLUTION"               "^[0-9]{1,3}$"
      "DPI"                          "^[0-9]{1,3}$"
      "default_MAP_RESOLUTION"       "91"
      "default_DPI"                  "91"
    END
  END

  RESOLUTION                         91
  DEFRESOLUTION                      91

  PROJECTION
     "init=epsg:28992"
  END

  #-------------------------------------------------------------------
  # UITVOERFORMATEN
  #-------------------------------------------------------------------

  OUTPUTFORMAT
    NAME           png
    DRIVER         "AGG/PNG"
    MIMETYPE       "image/png"
    IMAGEMODE      RGB
    EXTENSION      "png"
    FORMATOPTION   "INTERLACE=OFF"
    FORMATOPTION   "QUANTIZE_FORCE=ON"
  END

  OUTPUTFORMAT
    NAME           png8
    DRIVER         AGG/PNG8
    MIMETYPE       "image/png; mode=8bit"
    IMAGEMODE      RGB
    EXTENSION      "png"
    FORMATOPTION   "QUANTIZE_FORCE=on"
    FORMATOPTION   "QUANTIZE_COLORS=256"
    FORMATOPTION   "GAMMA=0.75"
  END

  OUTPUTFORMAT
    NAME        gif
    DRIVER      GD/GIF
    MIMETYPE    "image/gif"
    IMAGEMODE   PC256
    EXTENSION   "gif"
  END

  OUTPUTFORMAT
    NAME           "jpeg"
    DRIVER         AGG/JPEG
    MIMETYPE       "image/jpeg"
    IMAGEMODE      RGB
    EXTENSION      "jpg"
    FORMATOPTION   "GAMMA=0.75"
  END

  OUTPUTFORMAT
    NAME        svg
    DRIVER      CAIRO/SVG
    MIMETYPE    "image/svg+xml"
    IMAGEMODE   RGB
    EXTENSION   "svg"
  END

  OUTPUTFORMAT
    NAME        kml
    DRIVER      KML
    MIMETYPE    "application/vnd.google-earth.kml.xml"
    IMAGEMODE   RGB
    EXTENSION   "kml"
  END

  OUTPUTFORMAT
    NAME        kmz
    DRIVER      KMZ
    MIMETYPE    "application/vnd.google-earth.kmz"
    IMAGEMODE   RGB
    EXTENSION   "kmz"
  END

  OUTPUTFORMAT
    NAME           shapezip
    DRIVER         "OGR/ESRI Shapefile"
    FORMATOPTION   "STORAGE=memory"
    FORMATOPTION   "FORM=zip"
    FORMATOPTION   "FILENAME=result.zip"
  END

  OUTPUTFORMAT
    NAME           geojson
    DRIVER         "OGR/GEOJSON"
    MIMETYPE       "application/json; subtype=geojson; charset=utf-8"
    FORMATOPTION   "LCO:COORDINATE_PRECISION=7"
    FORMATOPTION   "STORAGE=stream"
    FORMATOPTION   "FORM=simple"
  END

  OUTPUTFORMAT
    NAME           "csv"
    DRIVER         "OGR/CSV"
    MIMETYPE       "text/csv"
    FORMATOPTION   "LCO:GEOMETRY=AS_WKT"
    FORMATOPTION   "STORAGE=memory"
    FORMATOPTION   "FORM=simple"
    FORMATOPTION   "FILENAME=result.csv"
  END

  OUTPUTFORMAT
    NAME           "gml"
    DRIVER         "OGR/GML"
    FORMATOPTION   "STORAGE=filesystem"
    FORMATOPTION   "FORM=multipart"
    FORMATOPTION   "FILENAME=result.gml"
  END

  OUTPUTFORMAT
    NAME           "spatialzip"
    DRIVER         "OGR/SQLITE"
    MIMETYPE       "application/zip"
    FORMATOPTION   "DSCO:SPATIALITE=YES"
    FORMATOPTION   "STORAGE=memory"
    FORMATOPTION   "FORM=zip"
    FORMATOPTION   "FILENAME=result.db.zip"
  END
 