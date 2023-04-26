    GROUP                    "objecten"

    INCLUDE                 "connection/dataservices.inc"
    DATA                    "geometrie FROM (
                                SELECT *
                                FROM leidingeninfrastructuur_klic_puntobjecten a
                                WHERE 
                                  a.thema = '%thema%'
                                ) AS query 
                              USING srid=28992 USING UNIQUE id"
    PROCESSING "CLOSE_CONNECTION=DEFER" # Use the same connection for all queried layers because they reside in the same db
    EXTENT 110000 476000 138000 494000
    TYPE                    POINT
    MAXSCALEDENOM 30000

    METADATA
      "wfs_group_title"           "Objecten Kadaster"
      "wfs_srs"             "EPSG:28992"
      "wfs_group_abstract"        "Objecten Kadaster"
      "wfs_enable_request"  "*"
      "wfs_extent"          "110000 476000 138000 494000"
      "wfs_use_default_extent_for_getfeature" "false" 
      "gml_featureid"       "id"
      "gml_include_items"   "all"
      "wms_group_title"           "Objecten Kadaster"
      "wms_enable_request"  "*"
      "wms_group_abstract"        ""
      "wms_srs"             "EPSG:28992"
      "wms_group_name"            "Objecten Kadaster"
      "wms_format"          "image/png"
      "wms_server_version"  "1.1.1"
      "wms_extent"          "110000 476000 138000 494000"
    END

    LABELITEM               "thema"