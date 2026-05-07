#!/usr/bin/env python

# Generates the ziektenplagenexotengroen mapfile.

from generate import block, header, p, q
import re

def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers = [
    ("Faunameubilair","Loopplank", "Loopplank", "loopplank"),
    ("Faunameubilair","Vogelhut", "Vogelhut", "vogelhut"),
    ("Faunameubilair","Vogelkijktoren", "Vogelkijktoren", "vogelkijktoren"),
    ("Faunameubilair","Vogelscherm", "Vogelscherm", "vogelscherm"),
    ("Faunaverblijfplaatsen","Bijenwand", "Bijenwand", "bijenwand"),
    ("Faunaverblijfplaatsen","Broeihoop", "Broeihoop", "broeihoop"),
    ("Faunaverblijfplaatsen","Insectenhotel", "Insectenhotel", "insectenhotel"),
    ("Faunaverblijfplaatsen","Ooievaarsnest", "Ooievaarsnest", "ooievaarsnest"),
    ("Faunaverblijfplaatsen","Vleermuiskast", "Vleermuiskast", "vleermuiskast"),
    ("Faunaverblijfplaatsen","Vleermuiskelder", "Vleermuiskelder", "vleermuiskelder"),
    ("Faunaverblijfplaatsen","Vleermuistoren", "Vleermuistoren", "vleermuistoren"),
    ("Faunaverblijfplaatsen","Winterverblijf", "Winterverblijf", "winterverblijf"),
    ("Faunavoorzieningen","Eekhoornbrug", "Eekhoornbrug", "eekhoornbrug"),
    ("Faunavoorzieningen","Faunaduiker", "Faunaduiker", "faunaduiker"),
    ("Faunavoorzieningen","Faunagoot", "Faunagoot", "faunagoot"),
    ("Faunavoorzieningen","Faunapassage", "Faunapassage", "faunapassage"),
    ("Faunavoorzieningen","Faunarichel", "Faunarichel", "faunarichel"),
    ("Faunavoorzieningen","Faunatunnel", "Faunatunnel", "faunatunnel"),
    ("Faunavoorzieningen","Faunauittreedplaats", "FaunaUittreedplaats", "faunauittreedplaats"),
    ("Faunavoorzieningen","Faunawand", "Faunawand", "faunawand"),
    ("Faunavoorzieningen","Keienwal", "Keienwal", "keienwal"),
    ("Faunavoorzieningen","Stobbenwal", "Stobbenwal", "stobbenwal"),
    ("Faunavoorzieningen","Vispassage", "Vispassage", "vispassage"),
    ("Hekken","Amfibieenscherm", "Amfibieënscherm", "amfibieenscherm"),
    ("Hekken","Faunaraster", "Faunaraster", "faunaraster"),
    ("Wildroosters","Wildrooster", "Wildrooster", "wildrooster"),
    ("Poelen","Poel", "Poel", "#392FC5"),
    ("Ecologische gebieden","Verbindingszone", "Verbindingszone", "#27AE60"),
    ("Ecologische gebieden","Kerngebied", "Kerngebied", "#F2C94C")
        ]


header("Bor")

with block("MAP"):
    p("NAME", "ecologische_voorzieningen")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("team", "BOR")
            q("ows_title", "Ecologische Voorzieningen")
            q(
                "ows_abstract",
                "Deze collectie bevat ecologische voorzieningen binnen gemeente Amsterdam. Dit zijn zowel ecologische objecten als ecologische gebieden. De ecologische objecten, zoals eekhoornbruggen en vispassages, zijn bedoeld voor dieren in de stad en zorgen ervoor dat zij zich veilig kunnen verplaatsen tussen verschillende leefgebieden. De ecologische gebieden zijn gericht op het vergroten van de biodiversiteit en zijn onderverdeeld in kerngebieden en verbindingszones. Kerngebieden bieden geschikte omstandigheden voor de permanente vestiging van soorten. Verbindingszones bieden geschikte omstandigheden voor tijdelijk verblijf, verbinden de kerngebieden met elkaar waardoor het leefgebied vergroot",
            )
            q("wms_extent", "100000 450000 150000 500000")
    with block("LEGEND"):
        p("STATUS ON")
        p("KEYSIZE 15 15")


    for group, name, filter, icon in layers:
        with block("LAYER"):
            p("NAME", name)
            p("GROUP", slugify(group))
            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")

            #niet echt trots op deze if statements, door deze aanpak is het heel makkelijk aanpasbaar, maar alle functies zijn anders.
            if group == "Faunameubilair":
                p(
                    "DATA",
                    "geometrie_punt FROM"
                    f" (SELECT * FROM public.ecologie_faunameubilair_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
                type = 'point'
            if group == "Faunaverblijfplaatsen":
                p(
                    "DATA",
                    "geometrie_punt FROM"
                    f" (SELECT * FROM public.ecologie_faunaverblijfplaatsen_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
                type = 'point'
            if group == "Faunavoorzieningen":
                p(
                    "DATA",
                    "geometrie_punt FROM"
                    f" (SELECT * FROM public.ecologie_faunavoorzieningen_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
                type = 'point'
            if group == "Hekken":
                p(
                    "DATA",
                    "geometrie_punt FROM"
                    f" (SELECT * FROM objectenopenbareruimte_hekken_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                ) 
                p("TYPE POINT")
                type = 'point'
            if group == "Wildroosters":
                p(
                    "DATA",
                    "geometrie_punt FROM"
                    f" (SELECT * FROM public.objectenopenbareruimte_roosters_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
                type = 'point'
            if group == "Poelen":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.objectenopenbareruimte_waterobjecten_v1 where type_gedetailleerd = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POLYGON")
                type = 'polygon'
            if group == "Ecologische gebieden":
                if name == 'Verbindingszone':
                    p(
                        "DATA",
                        "geometrie FROM"
                        f" (SELECT geometrie, id FROM public.ecologie_verbindingszones_v3) AS sub"
                        " USING srid=28992 USING UNIQUE id"
                    )
                if name == 'Kerngebied':
                    p(
                        "DATA",
                        "geometrie FROM"
                        f" (SELECT geometrie, id FROM public.ecologie_kerngebieden_v3) AS sub"
                        " USING srid=28992 USING UNIQUE id"
                    )
                p("TYPE POLYGON")
                type = 'polygon'

            with block("METADATA"):
                q("wfs_enable_request", "!*")
                q("ows_title", name)
                q("wms_enable_request", "*")
                q("ows_abstract", "Ecologische voorzieningen amsterdam")
                q("wms_format", "image/png")
                q("ows_group_title", group)


            with block("CLASS"):
                p("NAME", name)

                if type == 'polygon':
                    with block("STYLE"):
                        p("COLOR", icon)
                        p("OPACITY", 20) 

                    with block("STYLE"):
                        p("OUTLINECOLOR ", icon)
                        p("WIDTH ", 2)

                else:
                    with block("STYLE"):
                        p("SYMBOL", icon)
                        p("SIZE", 20)
