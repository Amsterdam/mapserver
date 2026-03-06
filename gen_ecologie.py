#!/usr/bin/env python

# Generates the ziektenplagenexotengroen mapfile.

from generate import block, header, p, q
import re

def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers = [
    ("Faunameubilair","Loopplank", "Loopplank", "aanwezig_laag"),
    ("Faunameubilair","Vogelhut", "Vogelhut", "deels_bestreden"),
    ("Faunameubilair","Vogelkijktoren", "Vogelkijktoren", "niet_in_beheer"),
    ("Faunameubilair","Vogelscherm", "Vogelscherm", "aanwezig_urgent"),
    ("Faunaverblijfplaatsen","Bijenwand", "Bijenwand", "gemeld"),
    ("Faunaverblijfplaatsen","Broeihoop", "Broeihoop", "bestreden"),
    ("Faunaverblijfplaatsen","Insectenhotel", "Insectenhotel", "niet_aanwezig"),
    ("Faunaverblijfplaatsen","Ooievaarsnest", "Ooievaarsnest", "niet_bereikbaar"),
    ("Faunaverblijfplaatsen","Vleermuiskast", "Vleermuiskast", "aanwezig_standaard"),
    ("Faunaverblijfplaatsen","Vleermuiskelder", "Vleermuiskelder", "preventief"),
    ("Faunaverblijfplaatsen","Vleermuistoren", "Vleermuistoren", "aanwezig_standaard"),
    ("Faunaverblijfplaatsen","Winterverblijf", "Winterverblijf", "preventief"),
    ("Faunavoorziening","Eekhoornbrug", "Eekhoornbrug", "preventief"),
    ("Faunavoorziening","Faunaduiker", "Faunaduiker", "preventief"),
    ("Faunavoorziening","Faunagoot", "Faunagoot", "preventief"),
    ("Faunavoorziening","Faunapassage", "Faunapassage", "preventief"),
    ("Faunavoorziening","Faunarichel", "Faunarichel", "preventief"),
    ("Faunavoorziening","Faunatunnel", "Faunatunnel", "preventief"),
    ("Faunavoorziening","Faunauittreedplaats", "Faunauittreedplaats", "preventief"),
    ("Faunavoorziening","Faunawand", "Faunawand", "preventief"),
    ("Faunavoorziening","Keienwal", "Keienwal", "preventief"),
    ("Faunavoorziening","Stobbenwal", "Stobbenwal", "preventief"),
    ("Faunavoorziening","Vispassage", "Vispassage", "preventief"),
    ("Hekken","Amfibiënscherm", "Amfibiënscherm", "preventief"),
    ("Hekken","Faunaraster", "Faunaraster", "preventief"),
    ("Wildroosters","Wildrooster", "Wildrooster", "preventief"),
    ("Poelen","Poel", "Poel", "preventief"),
    ("Ecologische gebieden","Verbindingszone", "Verbindingszone", "preventief"),
    ("Ecologische gebieden","Kerngebied", "Kerngebied", "preventief")
        ]


header("Bor")

with block("MAP"):
    p("NAME", "ecologie")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("team", "BOR")
            q("ows_title", "Ecologie")
            q(
                "ows_abstract",
                "Deze collectie bevat ecologische voorzieningen binnen gemeente Amsterdam. Dit zijn zowel ecologische objecten als ecologische gebieden. De ecologische objecten, zoals eekhoornbruggen en vispassages, zijn bedoeld voor dieren in de stad en zorgen ervoor dat zij zich veilig kunnen verplaatsen tussen verschillende leefgebieden. De ecologische gebieden zijn gericht op het vergroten van de biodiversiteit en zijn onderverdeeld in kerngebieden en verbindingszones. Kerngebieden bieden geschikte omstandigheden voor de permanente vestiging van soorten. Verbindingszones bieden geschikte omstandigheden voor tijdelijk verblijf, verbinden de kerngebieden met elkaar waardoor het leefgebied vergroot",
            )
            q("wms_extent", "100000 450000 150000 500000")

# dit stuk is voor de eikenprogressierups
    for group, name, filter, icon in layers:
        with block("LAYER"):
            p("NAME", name)
            p("GROUP", slugify(group))
            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")

            #hier voor de gewone processierups
            if group == "Faunameubilair":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.ecologie_faunameubilair_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
            if group == "Faunaverblijfplaatsen":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.ecologie_faunaverblijfplaatsen_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
            if group == "Faunavoorziening":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.ecologie_Faunavoorziening_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
            if group == "Hekken":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.ecologie_roosters_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
            if group == "Roosters":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.ecologie_roosters_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")
            if group == "Poelen":
                p(
                    "DATA",
                    "geometrie FROM"
                    f" (SELECT * FROM public.ecologie_waterobjecten_v1 where type = '{filter}') AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POLYGON")
            if group == "Ecologische gebieden":
                if name == 'Verbindingszone':
                    p(
                        "DATA",
                        "geometrie FROM"
                        f" (SELECT * FROM public.ecologie_verbindingzones_v3 where type = '{filter}') AS sub"
                        " USING srid=28992 USING UNIQUE id"
                    )
                elif name == 'Kerngebied':
                    p(
                        "DATA",
                        "geometrie FROM"
                        f" (SELECT * FROM public.ecologie_kerngebieden_v3 where type = '{filter}') AS sub"
                        " USING srid=28992 USING UNIQUE id"
                    )
                p("TYPE POLYGON")

            with block("METADATA"):
                q("wfs_enable_request", "!*")
                q("ows_title", name)
                q("wms_enable_request", "*")
                q("ows_abstract", "Ecologie amsterdam")
                q("wms_format", "image/png")
                q("ows_group_title", group)


            with block("CLASS"):
                p("NAME", name)

            with block("STYLE"):
                p("SYMBOL", icon)
                p("SIZE", 20)

            #hier voor de preventief processierups
            if group == "Eikenprocessierups Preventief":
                p(
                    "DATA",
                    "geometrie FROM"
                    # This subquery appears to do nothing, but it actually restricts
                    # the fields that mapserver sees.
                    " (select id, boom_id, gbd_buurt_id, geometrie, aantal_behandelingen_eikenprocessierups, geplande_uitvoeringsdatum_na, geplande_uitvoeringsdatum_voor,lastupdate, soortnaam, uiterste_uitvoeringsdatum_tweede_ronde, uitgevoerd_eerste_ronde_op, uitgevoerd_tweede_ronde_op from public.ziekte_plagen_exoten_groen_eikenprocessierups_preventief_v3) AS sub"
                    " USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")

                with block("METADATA"):
                    q("wfs_enable_request", "!*")
                    q("ows_title", name)
                    q("wms_enable_request", "*")
                    q("ows_abstract", "Eikenprocessierups Preventief in Amsterdam")
                    q("wms_format", "image/png")
                    q("ows_group_title", group)

                with block("CLASS"):
                    p("NAME", name)

                    with block("STYLE"):
                        p("SYMBOL", icon)
                        p("SIZE", 24)
                        p("OUTLINEWIDTH", 3)
                        p("OUTLINECOLOR", "#ffffff")

    
