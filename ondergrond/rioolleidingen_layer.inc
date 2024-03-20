    GROUP "rioolleidingen"
    INCLUDE                 "connection/dataservices.inc"
    PROCESSING "CLOSE_CONNECTION=DEFER" # Use the same connection for all queried layers because they reside in the same db
    TYPE                    LINE
    DATA                    "geometrie FROM (
                                SELECT objectnummer, geometrie, status, jaar_gelegd, soort, type_leiding, vorm, diameter, breedte, hoogte, materiaal, funderingstype, COALESCE(stelsel_type, 'Onbekend') AS stelsel_type
                                FROM leidingeninfrastructuur_waternet_rioolleidingen a
                                WHERE 
                                  ('%stelsel_type%' = 'Onbekend' AND a.stelsel_type ISNULL) OR
                                  a.stelsel_type = '%stelsel_type%'
                                ) AS query 
                              USING srid=7415 USING UNIQUE objectnummer"
                              
    METADATA
      "wfs_group_title"           "Rioolleidingen"
      "wfs_srs"             "EPSG:7415"
      "wfs_group_abstract"        "Rioolleidingen Waternet"
      "wfs_enable_request"  "*"
      "gml_featureid"       "objectnummer"
      "gml_include_items"   "all"
      "wms_group_title"           "Rioolleidingen Waternet"
      "wms_enable_request"  "*"
      "wms_group_abstract"        "Rioolleidingen Waternet"
      "wms_srs"             "EPSG:7415"
      "wms_group_name"            "Rioolleidingen Waternet"
      "wms_format"          "image/png"
      "wms_server_version"  "1.1.1"
      "wms_extent"          "100000 450000 150000 500000"
    END

    LABELITEM               "objectnummer"