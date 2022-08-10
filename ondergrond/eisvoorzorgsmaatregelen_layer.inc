    GROUP                    "eisvoorzorgsmaatregelen"

    INCLUDE                 "connection_dataservices.inc"
    DATA                    "geometrie FROM leidingeninfrastructuur_ligging_vlak_totaal USING srid=28992 USING UNIQUE id"
    EXTENT                  110000 476000 169999 520000
    PROCESSING              "CLOSE_CONNECTION=DEFER"
    TYPE                    POLYGON

    METADATA
      "wfs_group_title"     "Eisvoorzorgsmaatregelen Kadaster:"
      "wfs_srs"             "EPSG:28992"
      "wfs_group_abstract"  "Eisvoorzorgsmaatregelen Kadaster:"
      "wfs_enable_request"  "*"
      "wfs_extent"          "110000 476000 169999 52000"
      "gml_featureid"       "id"
      "gml_include_items"   "all"
      "wms_group_title"     "Eisvoorzorgsmaatregelen Kadaster:"
      "wms_enable_request"  "*"
      "wms_group_abstract"  ""
      "wms_srs"             "EPSG:28992"
      "wms_group_name"      "Eisvoorzorgsmaatregelen Kadaster:"
      "wms_format"          "image/png"
      "wms_server_version"  "1.1.1"
      "wms_extent"          "110000 476000 169999 52000"
    END

    LABELITEM               "thema"
    CLASSITEM               "thema"