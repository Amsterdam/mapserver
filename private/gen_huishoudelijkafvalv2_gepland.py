# Generates the huishoudelijkafval mapfile.

from generate import block, header, p, q
import re

def slugify(s: str) -> str:
    # Function to slugify strings (convert to lowercase and replace non-alphanumeric characters with underscores)
    s = s.replace("ë", "e")  # Replace special characters like 'ë' with 'e'
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()

# Define layers for huishoudelijkafval
layers = [
    {"group": "Huishoudelijkafvalcontainers gepland", "name": "gft_coordinaten_gepland", "filter": "[fractie_omschrijving] = 'GFT' AND [status] = 2", "symbol": "gfe", "title": "Gft"},
    {"group": "Huishoudelijkafvalcontainers gepland", "name": "textiel_coordinaten_gepland", "filter": "[fractie_omschrijving] = 'Textiel' AND [status] = 2", "symbol": "textiel", "title": "Textiel"},
    {"group": "Huishoudelijkafvalcontainers gepland", "name": "papier_coordinaten_gepland", "filter": "[fractie_omschrijving] = 'Papier' AND [status] = 2", "symbol": "papier", "title": "Papier"},
    {"group": "Huishoudelijkafvalcontainers gepland", "name": "glas_coordinaten_gepland", "filter": "[fractie_omschrijving] = 'Glas' AND [status] = 2", "symbol": "glas", "title": "Glas"},
    {"group": "Huishoudelijkafvalcontainers gepland", "name": "rest_coordinaten_gepland", "filter": "[fractie_omschrijving] = 'Rest' AND [status] = 2", "symbol": "rest", "title": "Rest"},
    {"group": "Huishoudelijkafvalcontainers gepland", "name": "brood_coordinaten_gepland", "filter": "[fractie_omschrijving] = 'Brood' AND [status] = 2", "symbol": "brood", "title": "Brood"}
]



# Generate the mapfile
header("Huishoudelijk Afvalcontainers gepland mapfile")

with block("MAP"):
    p("NAME", "huishoudelijkafvalcontainers_gepland")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("team", "BOR")
            q("ows_title", "Huishoudelijkafvalcontainers gepland")
            q("ows_abstract", "Kaart met gegevens over geplande huishoudelijk afvalcontainers in Amsterdam ")
            q("wms_extent", "4.58565 52.03560 5.31360 52.48769")
            q("wfs_extent", "4.58565 52.03560 5.31360 52.48769")
            q("gml_types", "auto")
            q("ows_onlineresource", "MAP_URL_REPLACE/maps/huishoudelijkafvalv2_gepland")            
    with block("LEGEND"):
            p("STATUS ON")
            p("KEYSIZE 30 30")

    # Generate layers for huishoudelijkafval containers
    for layer in layers:

        if layer["group"] == 'Huishoudelijkafvalcontainers gepland':
            with block("LAYER"):
                p("NAME", slugify(layer['name']))
                p("GROUP", f"{layer['group']}")
                with block("PROJECTION"):
                    q("init=epsg:28992")

                p("INCLUDE", "connection/dataservices.inc")
                if layer["name"] == 'onbekend_coordinaten':
                    p("DATA", f"geometrie FROM (select * FROM public.huishoudelijkafval_container_v2 where fractie_omschrijving is null and status = 2) as subquery USING srid=28992 USING UNIQUE id")
                else:
                    p("DATA", f"geometrie FROM public.huishoudelijkafval_container_v2 USING srid=28992 USING UNIQUE id")
                    print(f"FILTER ({layer['filter']})")
                p("TYPE POINT")
                p("MINSCALEDENOM", 10) 
                p("MAXSCALEDENOM", 400000)

                with block("METADATA"):
                    q("ows_title", layer['title'])
                    q("wfs_srs", "EPSG:28992")
                    q("wfs_abstract", f"{layer['title']} in Amsterdam")
                    q("wfs_enable_request", "*")

                p("LABELITEM", "id_nummer")

                with block ("CLASS"): 
                    p("NAME", f"{slugify(layer['title'])}")
                    p("TITLE", f"{layer['title']}")

                    with block("STYLE"):
                        p("SYMBOL", "stip")
                        p("COLOR", "#ffa200")
                        p("SIZE", 34)
                    with block("STYLE"):
                        p("SYMBOL", layer['symbol'])
                        p("SIZE", 30)

                    with block("LABEL"):
                        p("MAXSCALEDENOM 4000")
                        p("COLOR 102 102 102")
                        p("OUTLINECOLOR 255 255 255")
                        p("OUTLINEWIDTH 3")
                        p("FONT", "Ubuntu-M")
                        p("TYPE truetype")
                        p("SIZE 10")
                        p("POSITION AUTO")
                        p("PARTIALS FALSE")
                        p("OFFSET -60 10")