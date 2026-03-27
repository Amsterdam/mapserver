import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


###WARNING, deze py file genereerd alleen een STUKJE van de bag.map file, handmatig plakken is vereist..

layers = [
    ("Panden naar bouwjaar", "Onbekend", "([oorspronkelijk_bouwjaar] == 1005)", "#767676"),
    ("Panden naar bouwjaar", "Ouder dan 1800", "([oorspronkelijk_bouwjaar] < 1800 AND [oorspronkelijk_bouwjaar] != 1005)", "#610000"),
    ("Panden naar bouwjaar", "1800-1850", "([oorspronkelijk_bouwjaar] >= 1800 AND [oorspronkelijk_bouwjaar] < 1850)", "#A00000"),
    ("Panden naar bouwjaar", "1850-1900", "([oorspronkelijk_bouwjaar] >= 1850 AND [oorspronkelijk_bouwjaar] < 1900)", "#EC0000"),
    ("Panden naar bouwjaar", "1900-1930", "([oorspronkelijk_bouwjaar] >= 1900 AND [oorspronkelijk_bouwjaar] < 1930)",  "#F14600"),
    ("Panden naar bouwjaar", "1930-1945", "([oorspronkelijk_bouwjaar] >= 1930 AND [oorspronkelijk_bouwjaar] < 1945)", "#FBAA00"),
    ("Panden naar bouwjaar", "1945-1960", "([oorspronkelijk_bouwjaar] >= 1945 AND [oorspronkelijk_bouwjaar] < 1960)", "#FFE600"),
    ("Panden naar bouwjaar", "1960-1975", "([oorspronkelijk_bouwjaar] >= 1960 AND [oorspronkelijk_bouwjaar] < 1975)",  "#E5F2FC"),
    ("Panden naar bouwjaar", "1975-1985", "([oorspronkelijk_bouwjaar] >= 1975 AND [oorspronkelijk_bouwjaar] < 1985)", "#B1D9F5"),
    ("Panden naar bouwjaar", "1985-1995", "([oorspronkelijk_bouwjaar] >= 1985 AND [oorspronkelijk_bouwjaar] < 1995)", "#71BDEE"),
    ("Panden naar bouwjaar", "1995-2005", "([oorspronkelijk_bouwjaar] >= 1995 AND [oorspronkelijk_bouwjaar] < 2005)",  "#007EC5"),
    ("Panden naar bouwjaar", "2005-2015", "([oorspronkelijk_bouwjaar] >= 2005 AND [oorspronkelijk_bouwjaar] < 2015)", "#005FA3"),
    ("Panden naar bouwjaar", "2015-2025", "([oorspronkelijk_bouwjaar] >= 2015 AND [oorspronkelijk_bouwjaar] < 2025)", "#00467A"),
    ("Panden naar bouwjaar", "2025 of nieuwer", "([oorspronkelijk_bouwjaar] >= 2025)", "#002D4F"),
]


for group, layer_name, filter_value, color in layers:

    with block("LAYER"):
        sql = """geometrie FROM (SELECT id, oorspronkelijk_bouwjaar, geometrie, ligging_omschrijving, type_woonobject, ('https://api.data.amsterdam.nl/v1/bag/panden/' || identificatie || '/?volgnummer=' || volgnummer::text) AS uri FROM public.bag_panden_v1 WHERE coalesce(eind_geldigheid, now()) >= now() AND status_omschrijving NOT IN ('Niet gerealiseerd pand', 'Pand gesloopt', 'Pand ten onrechte opgevoerd')) AS subquery USING srid=28992 USING UNIQUE id"""
        layer_name_slug = slugify(layer_name)

        p("NAME", layer_name_slug)
        p("INCLUDE", "connection/dataservices.inc")
        p("DATA", sql)
        print (f"FILTER {filter_value}")
        p('GROUP', slugify(group))
        p("TYPE POLYGON")
        p('CLASSITEM       "oorspronkelijk_bouwjaar"')
        p('LABELITEM       "oorspronkelijk_bouwjaar"')
        p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")

        with block("PROJECTION"):
            q("init=epsg:28992")
        
        with block("METADATA"):
            q("ows_title", layer_name)
            q('ows_group_title', group)
            q("wms_include_items", "all")
            q("ows_abstract", "BAG panden van de gemeente Amsterdam, met leeftijd codering")
            q("gml_featureid", "ID")
            q("gml_geometries", "geometry")
            q("gml_geometry_type", "polygon")
            q("gml_include_items", "all")

        
        with block("CLASS"):
            p("NAME", layer_name)
            with block("STYLE"):
                p('COLOR', color)
                p("OPACITY", 50) 
                p('OUTLINECOLOR', color)
                p("WIDTH ", 1)
            with block("LABEL"):
                p("MINSCALEDENOM 10")
                p("MAXSCALEDENOM 1000")
                p("COLOR 0 0 0")
                p("OUTLINECOLOR 255 255 255")
                p("OUTLINEWIDTH 3")
                p("FONT", "Ubuntu-M")
                p("TYPE truetype")
                p("SIZE 10")
                p("POSITION AUTO")
                p("PARTIALS FALSE")
