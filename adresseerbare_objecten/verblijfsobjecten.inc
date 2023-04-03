# Shared definitions for layers in the verblijfsobjecten layergroup
# in adresseerbare_objecten.map
# 
# Verblijfsobjecten are filtered on status or gebruiksdoel.
# The layer that INCLUDEs this template parametrizes the query
# using run-time substitution.
VALIDATION
  "layertitle" "^.+$"
  "grouptitle" "^gebruiksdoel|status$"
  "status" "^[a-zA-Z() ]+|all$"
  "default_status" "all"
  "gebruiksdoel" "^[a-z ]+functie|all$"
  "default_gebruiksdoel" "all"
END
DEBUG 5

INCLUDE                 "connection_dataservices.inc"
DATA                    "geometrie FROM (
                            SELECT 
                              bv.id AS id,
                              bv.geometrie AS geometrie,
                              bv.status_omschrijving AS status,
                              bvg.omschrijving AS gebruiksdoel
                            FROM bag_verblijfsobjecten AS bv 
                            INNER JOIN bag_verblijfsobjecten_gebruiksdoel AS bvg
                            ON bv.id = bvg.parent_id
                            WHERE 
                              (lower(bv.status_omschrijving) = lower($1) OR $1 = 'all')
                              AND
                              (lower(bvg.omschrijving) = lower($2) OR $2 = 'all')
                            ) AS query 
                          USING srid=28992 USING UNIQUE id"
BINDVALS
  "1" "%status%"
  "2" "%gebruiksdoel%"
END
PROCESSING "CLOSE_CONNECTION=DEFER" # Use the same connection for all queried layers because they reside in the same db
EXTENT 110000 476000 138000 494000
TYPE                    POINT
MAXSCALEDENOM 8000

METADATA
    "wms_title" '%layertitle%'
    "wms_group_title" 'Verblijfsobjecten %grouptitle%'
    "wms_enable_request" "*"
    "wms_srs"             "EPSG:28992"
END