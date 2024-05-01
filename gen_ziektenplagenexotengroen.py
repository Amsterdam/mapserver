#!/usr/bin/env python

# Generates the ziektenplagenexotengroen mapfile.

from generate import block, header, p, q
import re

def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers_EPR = [
    ("Eikenprocessierups aanwezig (Laag)", "caterpillar_blue"),
    ("Eikenprocessierups deels bestreden", "tree_orange"),
    ("Niet in beheergebied Gemeente Amsterdam", "flag_black"),
    ("Eikenprocessierups aanwezig (Urgent)", "caterpillar_red"),
    ("Gemeld", "speechbubble"),
    ("Eikenprocessierups bestreden", "tree_green"),
    ("Geen Eikenprocessierups aanwezig", "tree_black"),
    ("Niet bereikbaar voor bestrijding", "flag_red"),
    ("Eikenprocessierups aanwezig (Standaard)", "caterpillar_orange"),
]

layers_JPD = [
    ("Japanse Duizendknoop Meldingen","Japanse Duizendknoop Meldingen Gemeld", "Gemeld", "gfe"),
    ("Japanse Duizendknoop Meldingen","Japanse Duizendknoop Meldingen Duizendknoop verwijderd", "Duizendknoop verwijderd", "brood")
]

header("Bor / Beeldschoon")

with block("MAP"):
    p("NAME", "ziektenplagenexotengroen")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Ziekte, plagen, exoten, groen")
            q(
                "ows_abstract",
                "Kaart met gegevens over ziekten, plagen en exoten in het groen in de gemeente Amsterdam",
            )
            q("wms_extent", "100000 450000 150000 500000")

# dit stuk is voor de eikenprogressierups
    for name, icon in layers_EPR:
        with block("LAYER"):
            p("NAME", name)
            p("GROUP", "eikenprocessierups")
            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")
            p(
                "DATA",
                "geometrie FROM"
                # This subquery appears to do nothing, but it actually restricts
                # the fields that mapserver sees.
                " (SELECT id, geometrie, urgentie_status_kaartlaag FROM public.ziekte_plagen_exoten_groen_eikenprocessierups WHERE ranking=1) AS sub"
                " USING srid=28992 USING UNIQUE id"
            )
            p("TYPE POINT")

            with block("METADATA"):
                q("wfs_enable_request", "!*")
                q("wms_title", name)
                q("wms_enable_request", "*")
                q("wms_abstract", "Eikenprocessierups Amsterdam")
                q("wms_srs", "EPSG:28992")
                q("wms_name", "Eikenprocessierups")
                q("wms_format", "image/png")
                q("wms_server_version", "1.3.0")
                q("ows_group_title", "Eikenprocessierups")

            p("LABELITEM", "urgentie_status_kaartlaag")
            p("CLASSITEM", "urgentie_status_kaartlaag")

            with block("CLASS"):
                p("NAME", name)
                p("EXPRESSION", name)

                with block("STYLE"):
                    p("SYMBOL", icon)
                    p("SIZE", 20)

    
    #Vanaf hier is het voor de japanse duizendknoop
    for group, name, filter, icon in layers_JPD:
        with block("LAYER"):
            p("NAME", slugify(name))
            p("GROUP", slugify(group))

            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")
            
            if 'Meldingen' in group:
                p(
                    "DATA",
                    "geometrie FROM public.ziekte_plagen_exoten_groen_japanseduizendknoop_meldingen USING srid=28992 USING UNIQUE id"
                )
            else:
                p(
                    "DATA",
                    "geometrie FROM public.ziekte_plagen_exoten_groen_japanseduizendknoop_inspecties USING srid=28992 USING UNIQUE id"
                )
            p("TYPE POINT")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            p("CLASSITEM", "status_kaartlaag")
            # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
            print (f'FILTER ("[status_kaartlaag]" = "{filter}")')
            
            with block("METADATA"):
                q("ows_title", name)
                q("wms_enable_request", "*")
                q("wms_abstract", "Japanse Duizendknoop Amsterdam")
                q("wms_srs", "EPSG:28992")
                q("ows_group_title", group)

            with block("CLASS"):
                p("NAME", name)

                with block("STYLE"):
                    p("SYMBOL", icon)
                    p("SIZE", 20)
