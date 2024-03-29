    GROUP                    "kabels_en_leidingen"

    INCLUDE                 "connection/dataservices.inc"
    DATA                    "geometrie FROM (
                                SELECT *
                                FROM leidingeninfrastructuur_klic_kabels_en_leidingen a
                                WHERE 
                                  a.thema = '%thema%'
                                ) AS query 
                              USING srid=28992 USING UNIQUE id"
    EXTENT                  110000 476394 138000 494000
    PROCESSING "CLOSE_CONNECTION=DEFER" # Use the same connection for all queried layers because they reside in the same db
    TYPE                    LINE
    MAXSCALEDENOM 30000
    METADATA
      "wfs_group_title"           "Kabels en Leidingen Kadaster"
      "wfs_srs"             "EPSG:28992"
      "wfs_group_abstract"        "Kabels en Leidingen Kadaster"
      "wfs_enable_request"  "*"
      "wfs_extent"          "110000 476394 138000 494000"
      "gml_featureid"       "id"
      "gml_include_items"   "all"
      "wms_group_title"           "Kabels en Leidingen Kadaster"
      "wms_enable_request"  "*"
      "wms_group_abstract"        ""
      "wms_srs"             "EPSG:28992"
      "wms_format"          "image/png"
      "wms_server_version"  "1.1.1"
      "wms_extent"          "110000 476394 138000 494000"
    END

    LABELITEM               "thema"
