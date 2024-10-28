# Generates the huishoudelijkafval mapfile.

from generate import block, header, p, q
import re

def slugify(s: str) -> str:
    # Function to slugify strings (convert to lowercase and replace non-alphanumeric characters with underscores)
    s = s.replace("ë", "e")  # Replace special characters like 'ë' with 'e'
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()

# Define layers for huishoudelijkafval
layers = [
    {"group": "afvalcontainers", "name": "gft_coordinaten", "filter": "[fractie_omschrijving] = 'GFT' AND [status] = 1", "symbol": "gft", "title": "Gftafvalcontainer"},
    {"group": "afvalcontainers", "name": "textiel_coordinaten", "filter": "[fractie_omschrijving] = 'Textiel' AND [status] = 1", "symbol": "textiel", "title": "Textielafvalcontainer"},
    {"group": "afvalcontainers", "name": "papier_coordinaten", "filter": "[fractie_omschrijving] = 'Papier' AND [status] = 1", "symbol": "papier", "title": "Papierafvalcontainer"},
    {"group": "afvalcontainers", "name": "glas_coordinaten", "filter": "[fractie_omschrijving] = 'Glas' AND [status] = 1", "symbol": "glas", "title": "Glasafvalcontainer"},
    {"group": "afvalcontainers", "name": "rest_coordinaten", "filter": "[fractie_omschrijving] = 'Rest' AND [status] = 1", "symbol": "rest", "title": "Restafvalcontainer"},
    {"group": "afvalcontainers", "name": "brood_coordinaten", "filter": "[fractie_omschrijving] = 'Brood' AND [status] = 1", "symbol": "brood", "title": "Broodafvalcontainer"},
    {"group": "afvalcontainers", "name": "onbekend_coordinaten", "filter": "fractie_omschrijving is null and status = 1", "symbol": "onbekend", "title": "Onbekend"},
    {"group": "kilogram", "name": "wegingen_rest", "filter": "[fractie_omschrijving] = 'Rest'","symbol": "stip","title": "Rest wegingen"},
    {"group": "kilogram", "name": "wegingen_glas", "filter": "[fractie_omschrijving] = 'Glas'","symbol": "stip","title": "Glas wegingen"},
    {"group": "kilogram", "name": "wegingen_papier", "filter": "[fractie_omschrijving] = 'Papier'","symbol": "stip","title": "Papier wegingen"},
    {"group": "kilogram", "name": "wegingen_plastic", "filter": "[fractie_omschrijving] = 'Plastic'","symbol": "stip","title": "Plastic wegingen"},
    {"group": "kilogram", "name": "wegingen_textiel", "filter": "[fractie_omschrijving] = 'Textiel'","symbol": "stip","title": "Textiel wegingen"},
    {"group": "kilogram", "name": "wegingen_grof", "filter": "[fractie_omschrijving] = 'Grof'","symbol": "stip","title": "Grof wegingen"},
    {"group": "kilogram", "name": "wegingen_PMD", "filter": "[fractie_omschrijving] = 'PMD'","symbol": "stip","title": "PMD wegingen"},
    {"group": "kilogram", "name": "wegingen_brood", "filter": "[fractie_omschrijving] = 'Brood'","symbol": "stip","title": "Brood wegingen"},
    {"group": "kilogram", "name": "wegingen_onbekend", "filter": "[fractie_omschrijving] is null","symbol": "stip","title": "Onbekend wegingen"},
    { "group": "pand_loopafstand", "name": "pand_loopafstand_rest", "filter": "[fractie_omschrijving] = 'Rest'", "symbol": "rest", "title": "Loopafstand tot restafvalcontainer"}
]

weight_ranges = [
    {"name": "< 50 kg", "expression": "[netto_gewicht] < 50", "color": (0, 104, 55)},
    {"name": "< 90 kg", "expression": "[netto_gewicht] < 90", "color": (26, 152, 80)},
    {"name": "< 130 kg", "expression": "[netto_gewicht] < 130", "color": (102, 189, 99)},
    {"name": "< 170 kg", "expression": "[netto_gewicht] < 170", "color": (166, 217, 106)},
    {"name": "< 210 kg", "expression": "[netto_gewicht] < 210", "color": (217, 239, 139)},
    {"name": "< 260 kg", "expression": "[netto_gewicht] < 260", "color": (254, 224, 139)},
    {"name": "< 310 kg", "expression": "[netto_gewicht] < 310", "color": (253, 174, 97)},
    {"name": "< 390 kg", "expression": "[netto_gewicht] < 390", "color": (244, 109, 67)},
    {"name": "< 500 kg", "expression": "[netto_gewicht] < 500", "color": (215, 48, 39)},
    {"name": "> 500 kg", "expression": "[netto_gewicht] >= 500", "color": (165, 0, 38)}
]
#hier moet nog iets anders, deze zijn niet altijd deze intervallen.......
loopafstanden_ranges = [
    {"name": "<= 30 m", "expression": "[loopafstand_categorie_omschrijving] eq '0 - 30 M'", "color": (50, 114, 48)},
    {"name": "30 - 90 m", "expression": "[loopafstand_categorie_omschrijving] eq '30 - 90 M'", "color": (77, 175, 74)},
    {"name": "90 - 120 m", "expression": "[loopafstand_categorie_omschrijving] eq '90 - 120 M'", "color": (157, 175, 157)},
    {"name": "120 - 150 m", "expression": "[loopafstand_categorie_omschrijving] eq '120 - 150 M'", "color": (255, 127, 0)},
    {"name": "150 - 210 m", "expression": "[loopafstand_categorie_omschrijving] eq '150 - 210 M'", "color": (255, 75, 0)},
    {"name": "210 - 1000 m", "expression": "[loopafstand_categorie_omschrijving] eq '210 - 1000 M'", "color": (110, 110, 110)},
    {"name": "vanaf 1000 m", "expression": "[loopafstand_categorie_omschrijving] eq 'meer dan 1000 M'", "color": (204, 204, 204)}
]

# Generate the mapfile
header("Huishoudelijk Afval Mapfile")

with block("MAP"):
    p("NAME", "huishoudelijkafval")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "afvalcontainers")
            q("ows_abstract", "Kaart met gegevens over huishoudelijk afvalcontainers in Amsterdam")
            q("wms_extent", "4.58565 52.03560 5.31360 52.48769")
            q("wfs_extent", "4.58565 52.03560 5.31360 52.48769")
            q("gml_types", "auto")

    # Generate layers for huishoudelijkafval containers
    for layer in layers:
        with block("LAYER"):
            p("NAME", slugify(layer['name']))
            p("GROUP", "afvalcontainers")
            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")
            p("DATA", f"geometrie FROM public.huishoudelijkafval_container USING srid=28992 USING UNIQUE id")
            p("FILTER", layer['filter'])
            p("TYPE POINT")
            p("MINSCALEDENOM", 10)
            p("MAXSCALEDENOM", 400000)

            with block("METADATA"):
                q("wfs_title", layer['title'])
                q("wfs_srs", "EPSG:28992")
                q("wfs_abstract", f"{layer['title']} in Amsterdam")
                q("wfs_enable_request", "*")

            p("LABELITEM", "id_nummer")

            with block ("CLASS"): 
                p("NAME", f"{slugify(layer['title'])}")
                p("TITLE", f"{layer['title']}")

            with block("STYLE"):
                p("SYMBOL", layer['symbol'])
                p("SIZE", 20)

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
