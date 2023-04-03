# Shared definitions for layers in the ligplaatsen layergroup
# in adresseerbare_objecten.map
# 
# ligplaatsen are filtered on gebruiksdoel.
# The layer that INCLUDEs this template parametrizes the query
# using run-time substitution.
GROUP                    "ligplaatsen"
VALIDATION
  "layertitle" "^.+$"
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
                            FROM bag_ligplaatsen AS bv 
                            INNER JOIN bag_ligplaatsen_gebruiksdoel AS bvg
                            ON bv.id = bvg.parent_id
                            WHERE 
                              (lower(bvg.omschrijving) = lower($1) OR $1 = 'all')
                            ) AS query 
                          USING srid=28992 USING UNIQUE id"
BINDVALS
  "1" "%gebruiksdoel%"
END
PROCESSING "CLOSE_CONNECTION=DEFER" # Use the same connection for all queried layers because they reside in the same db
EXTENT 110000 476000 138000 494000
TYPE                    POLYGON

METADATA
    "wms_title" '%layertitle%'
    "wms_group_title" 'Ligplaatsen'
    "wms_enable_request" "*"
    "wms_srs"             "EPSG:28992"
END