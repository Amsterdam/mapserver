#!/usr/bin/env python

# Generates the ziektenplagenexotengroen mapfile.

from generate import block, header, p, q
import re

def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers_EPR = [
    ("Eikenprocessierups","Eikenprocessierups aanwezig (Laag)", "Eikenprocessierups aanwezig (Laag)", "caterpillar_blue"),
    ("Eikenprocessierups","Eikenprocessierups deels bestreden", "Eikenprocessierups deels bestreden", "tree_orange"),
    ("Eikenprocessierups","Niet in beheergebied Gemeente Amsterdam", "Niet in beheergebied Gemeente Amsterdam", "flag_black"),
    ("Eikenprocessierups","Eikenprocessierups aanwezig (Urgent)", "Eikenprocessierups aanwezig (Urgent)", "caterpillar_red"),
    ("Eikenprocessierups","Eikenprocessierups gemeld", "Gemeld", "speechbubble"),
    ("Eikenprocessierups","Eikenprocessierups bestreden", "Eikenprocessierups bestreden", "tree_green"),
    ("Eikenprocessierups","Geen Eikenprocessierups aanwezig", "Geen Eikenprocessierups aanwezig", "tree_black"),
    ("Eikenprocessierups","Niet bereikbaar voor bestrijding", "Niet bereikbaar voor bestrijding", "flag_red"),
    ("Eikenprocessierups","Eikenprocessierups aanwezig (Standaard)", "Eikenprocessierups aanwezig (Standaard)", "caterpillar_orange"),
    ("Eikenprocessierups Preventief","Eikenprocessierups Preventief", "Eikenprocessierups Preventief", "preventief"),

]

layers_JPD = [
    ("Japanse Duizendknoop Meldingen", "Duizendknoop gemeld (Meldingen)", "Gemeld", "JPD_Gemeld"),
    ("Japanse Duizendknoop Meldingen", "Duizendknoop aanwezig, niet bereikbaar (Meldingen)", "Duizendknoop aanwezig, niet bereikbaar", "JPD_Duizendknoop_aanwezig_niet_bereikbaar"),
    ("Japanse Duizendknoop Meldingen", "Duizendknoop aanwezig (Meldingen)", "Duizendknoop aanwezig", "JPD_Duizendknoop_aanwezig"),
    ("Japanse Duizendknoop Meldingen", "Duizendknoop in bestrijding (Meldingen)", "In bestrijding", "JPD_In_bestrijding"),
    ("Japanse Duizendknoop Meldingen", "Duizendknoop monitoring (Meldingen)", "Monitoring", "JPD_Monitoring"),
    ("Japanse Duizendknoop Meldingen", "Duizendknoop verwijderd (Meldingen)", "Duizendknoop verwijderd", "JPD_Duizendknoop_verwijderd"),

    ("Japanse Duizendknoop Inspecties", "Duizendknoop gemeld (Inspecties)", "Gemeld", "#004698"),
    ("Japanse Duizendknoop Inspecties", "Duizendknoop aanwezig, niet bereikbaar (Inspecties)", "Duizendknoop aanwezig, niet bereikbaar", "#767676"),
    ("Japanse Duizendknoop Inspecties", "Duizendknoop aanwezig (Inspecties)", "Duizendknoop aanwezig", "#ec0000"),
    ("Japanse Duizendknoop Inspecties", "Duizendknoop in bestrijding (Inspecties)", "In bestrijding", "#fe9100"),
    ("Japanse Duizendknoop Inspecties", "Duizendknoop Monitoring (Inspecties)", "Monitoring", "#029ce6"),
    ("Japanse Duizendknoop Inspecties", "Duizendknoop verwijderd (Inspecties)", "Duizendknoop verwijderd", "#00a03c")
]

layers_JPD_percelen = [
    ("Japanse Duizendknoop Percelen", "Gemeente Amsterdam", "Gemeente Amsterdam", "#E6194B"),
    ("Japanse Duizendknoop Percelen", "Overige gemeenten", "Overige gemeenten, niet bereikbaar", "#3CB44B"),
    ("Japanse Duizendknoop Percelen", "Overige natuurlijke personen", "Overige natuurlijke personen", "#FFE119"),
    ("Japanse Duizendknoop Percelen", "Overige niet-natuurlijke personen", "Overige niet-natuurlijke personen", "#0082C8"),
    ("Japanse Duizendknoop Percelen", "Provincies", "Provincies", "#F58231"),
    ("Japanse Duizendknoop Percelen", "Spoorwegen/ProRail", "Spoorwegen/ProRail", "#911EB4"),
    ("Japanse Duizendknoop Percelen", "Staat", "Staat", "#46F0F0"),
    ("Japanse Duizendknoop Percelen", "Verenigingen van eigenaren", "Verenigingen van eigenaren", "#F032E6"),
    ("Japanse Duizendknoop Percelen", "Waterschappen", "Waterschappen", "#D2F53C"),
    ("Japanse Duizendknoop Percelen", "Woningbouwcorporaties", "Woningbouwcorporaties", "#FABEBE"),
    ("Japanse Duizendknoop Percelen", "meerdere categorieën", "meerdere categorieën", "#008080"),
    ("Japanse Duizendknoop Percelen", "onbekend", "onbekend", "#E6BEFF")
]

header("Bor")

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
    for group, name, filter, icon in layers_EPR:
        with block("LAYER"):
            p("NAME", name)
            p("GROUP", slugify(group))
            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")

            #hier voor de gewone processierups
            if group == "Eikenprocessierups":
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
                    q("ows_title", name)
                    q("wms_enable_request", "*")
                    q("ows_abstract", "Eikenprocessierups Amsterdam")
                    q("wms_format", "image/png")
                    q("ows_group_title", group)

                p("LABELITEM", "urgentie_status_kaartlaag")
                p("CLASSITEM", "urgentie_status_kaartlaag")

                with block("CLASS"):
                    p("NAME", name)
                    p("EXPRESSION", filter)

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
                    " (select id, boom_id, gbd_buurt_id, geometrie, aantal_behandelingen_eikenprocessierups, geplande_uitvoeringsdatum_na, geplande_uitvoeringsdatum_voor,lastupdate, soortnaam, uiterste_uitvoeringsdatum_tweede_ronde, uitgevoerd_eerste_ronde_op, uitgevoerd_tweede_ronde_op from public.ziekte_plagen_exoten_groen_eikenprocessierups_preventief) AS sub"
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

    
    #Vanaf hier is het voor de japanse duizendknoop
    for group, title, filter, icon_color in layers_JPD:
        with block("LAYER"):
            p("NAME", slugify(title))
            p("GROUP", slugify(group))

            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")
            
    #hier voor de meldingen
            if 'Meldingen' in group:
                p(
                    "DATA",
                    "geometrie FROM public.ziekte_plagen_exoten_groen_japanseduizendknoop_meldingen USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POINT")

                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
                p("CLASSITEM", "status_kaartlaag")
                # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
                print (f'FILTER ("[status_kaartlaag]" = "{filter}")')
                
                with block("METADATA"):
                    q("ows_title", title)
                    q("wms_enable_request", "*")
                    q("ows_abstract", "Japanse Duizendknoop Amsterdam")
                    q("wms_srs", "EPSG:28992")
                    q("ows_group_title", group)

                with block("CLASS"):
                    p("NAME", slugify(title))

                    with block("STYLE"):
                        p("SYMBOL", icon_color)
                        p("SIZE", 20)

    #hier voor de inspecties    
            if 'Inspecties' in group:
                p(
                    "DATA",
                    "geometrie FROM public.ziekte_plagen_exoten_groen_japanseduizendknoop_inspecties USING srid=28992 USING UNIQUE id"
                )
                p("TYPE POLYGON")

                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
                p("CLASSITEM", "status_kaartlaag")
                # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
                print (f'FILTER ("[status_kaartlaag]" = "{filter}")')
                
                with block("METADATA"):
                    q("ows_title", title)
                    q("wms_enable_request", "*")
                    q("ows_abstract", "Japanse Duizendknoop Amsterdam")
                    q("wms_srs", "EPSG:28992")
                    q("ows_group_title", group)

                with block("CLASS"):
                    p("NAME", slugify(title))

                    with block("STYLE"):

                        p("COLOR", icon_color)
                        p("OPACITY", 20) 

                    with block("STYLE"):
                        p("OUTLINECOLOR ", icon_color)
                        p("WIDTH ", 2)


    #hier voor de percelen
    with block("LAYER"):
        p("NAME", 'japanse_duizendknoop_percelen')
        p("GROUP", 'japanse_duizendknoop_percelen')

        with block("PROJECTION"):
            q("init=epsg:28992")

        p("INCLUDE", "connection/dataservices.inc") 
        p(
            "DATA",
            "geometrie FROM public.ziekte_plagen_exoten_groen_japanseduizendknoop_percelen USING srid=28992 USING UNIQUE id"
        )
        p("TYPE POLYGON")

        p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
        
        with block("METADATA"):
            q("ows_title", 'Japanse Duizendknoop Percelen')
            q("wms_enable_request", "*")
            q("ows_abstract", "Japanse Duizendknoop Amsterdam")
            q("wms_srs", "EPSG:28992")
            q("ows_group_title", 'Japanse Duizendknoop Percelen')

        for group, title, filter, icon_color in layers_JPD_percelen:
            with block("CLASS"):
                p("NAME", slugify(title))
                p("TITLE", title)
                print (f'EXPRESSION ("[categorie]" = "{filter}")')

                with block("STYLE"):

                    p("COLOR", icon_color)
                    p("OPACITY", 20) 

                with block("STYLE"):
                    p("OUTLINECOLOR ", icon_color)
                    p("WIDTH ", 2)
                
                with block("LABEL"):
                    p("EXPRESSION ([ligt_op_percelen] > 1)") 
                    p("TEXT '[deel_van_inspectievlak]% van insp.: [jdk_inspectielak_id]'") 
                    p("MAXSCALEDENOM 750")
                    p("COLOR 0 0 0")
                    p("OUTLINECOLOR 255 255 255")
                    p("OUTLINEWIDTH 1.5")
                    p("FONT", "Ubuntu-M")
                    p("TYPE truetype")
                    p("SIZE 8")
                    p("POSITION AUTO")
                    p("PARTIALS FALSE")

                with block("LABEL"):
                    p("EXPRESSION ([ligt_op_percelen] = 1)") 
                    p("TEXT 'insp.: [jdk_inspectielak_id]'") 
                    p("MAXSCALEDENOM 750")
                    p("COLOR 0 0 0")
                    p("OUTLINECOLOR 255 255 255")
                    p("OUTLINEWIDTH 1.5")
                    p("FONT", "Ubuntu-M")
                    p("TYPE truetype")
                    p("SIZE 8")
                    p("POSITION AUTO")
                    p("PARTIALS FALSE")