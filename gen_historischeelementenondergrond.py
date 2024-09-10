import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers = [
    ("Bodemgebruik en obstakels", "Boerderij", "Boerderij", ('#ebdc56', False)),    #VLAK zit in 'objecten' tabel
    ("Bodemgebruik en obstakels", "Defensieterrein", "Defensieterrein", ('#d5587c', False)),
    ("Bodemgebruik en obstakels", "Fabriek/bedrijventerrein", "Fabriek/bedrijventerrein", ('#a78409', False)),
    ("Bodemgebruik en obstakels", "Gebouw", "Gebouw", ('#0e6f99', False)),
    ("Bodemgebruik en obstakels", "Glastuinbouw", "Glastuinbouw", ('#9bca54', '#9bca54')),
    ("Bodemgebruik en obstakels", "Object", "Object", ('#03cea2', False)),
    ("Bodemgebruik en obstakels", "Overig", "Overig", ('#d00ee5', False)),
    ("Bodemgebruik en obstakels", "Spoorwegemplacement", "Spoorwegemplacement", ('#ae95b9', False)),
    ("Bodemgebruik en obstakels", "Stookruimte/olietank", "Stookruimte/olietank", ('#713dbe', False)),\
    ("Bodemgebruik en obstakels", "Tram- en busremises", "Tram en busremises", ('#3a15e1', '#3a15e1')),
    ("Bodemgebruik en obstakels", "Volkstuinen", "Volkstuinen", ('#06d3f7', False)),
    ("Lijnvormige obstakels ", "Gasbuis", "Gasbuis", ('#bfb479', True)), #LIJN zit in 'kabels en leidingen'
    ("Lijnvormige obstakels ", "Grondkering", "Grondkering", ('#d7650e',False)),
    ("Lijnvormige obstakels ", "Kabel", "Kabel", ('#d67814', True)),
    ("Lijnvormige obstakels ", "Mantelbuis", "Mantelbuis", ('#79e0d4', True)),
    ("Lijnvormige obstakels ", "Persleiding", "Persleiding", ('#20a620', True)),
    ("Lijnvormige obstakels ", "Riool", "Riool", ('#0e5129', True)),
    ("Lijnvormige obstakels ", "Spoorweg", "Spoorweg", ('#232323', True)),
    ("Lijnvormige obstakels ", "Waterleiding", "Waterleiding", ('#3a15e1', True)),
    ("Dempingen en ophogingen", "Demping", "Demping", ('#e4d62e', False)), #dit zit uiteraard in dempingen en ophogingen
    ("Dempingen en ophogingen", "Depot/stort", "Depot/stort", ('#ce7263', False)),
    ("Dempingen en ophogingen", "Dijk", "Dijk", ('#ce7263', False)),
    ("Dempingen en ophogingen", "Ophoging", "Ophoging", ('#ce7263', False))
]


with block("MAP"):
    p("NAME", "historischebodeminformatie")
    p("INCLUDE", "header.inc")


    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Historische Bodeminformatie")
            #q("ows_onlineresource", "MAP_URL_REPLACE/maps/historischeelementenondergrond")
            q("ows_abstract", "Historische Bodeminformatie",)

    
    for group, layer_name, filter_value, colors in layers:

        if group == 'Bodemgebruik en obstakels':

            with block("LAYER"):
                sql = f"geometrie from (SELECT * FROM historische_bodeminformatie_objecten where categorie = '{filter_value}') as subquery USING srid=28992 USING UNIQUE id"
                

                layer_name_slug = slugify(layer_name)

                p("NAME", layer_name_slug)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p('GROUP', slugify(group))
                p("TYPE POLYGON")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")

                with block("PROJECTION"):
                    q("init=epsg:28992")
                
                with block("METADATA"):
                    q("ows_title", layer_name)
                    q('ows_group_title', group)
                    q("wms_include_items", "all")
                    q("ows_abstract", "Bodemgebruik en obstakels")
                    q("gml_featureid", "id")
                    q("gml_geometries", "geometry")
                    q("gml_geometry_type", "polygon")
                    q("gml_include_items", "all")
                    q("gml_types", "auto")


                with block("CLASS"):
                    p("NAME", f"{layer_name_slug}")
                    p("TITLE", f"{layer_name}")

                    with block("STYLE"):
                        p(f'COLOR "{colors[0]}"')
                        p("OPACITY", 40) 
                        p(f'OUTLINECOLOR "{colors[0]}"')
                        p("WIDTH ", 2)
                    
                    if colors[1] is not False:
                        with block("STYLE"):
                            p('SYMBOL "hatch"')
                            p(f'COLOR "{colors[1]}"')
                            p("OPACITY", 100) 
                            p('ANGLE', 45)
                            p('GAP', 4)
                            p("WIDTH ", 2)


        # if group == 'Servicegebiedenlocatie':

        #     with block("LAYER"):
        #         sql = f"geometrie from (SELECT *, (regexp_matches(id, '[0-9](?!.*[0-9])'))[1] AS last_numeric_digit FROM huishoudelijkafval_servicegebieden_locatie where cluster_fractie_omschrijving = '{filter_value}') as subquery USING srid=28992 USING UNIQUE id"
                

        #         layer_name_slug = slugify(layer_name)

        #         p("NAME", layer_name_slug)
        #         p("INCLUDE", "connection/dataservices.inc")
        #         p("DATA", sql)
        #         p('GROUP', slugify(group))
        #         p("TYPE POINT")
        #         # p("MINSCALEDENOM 10")
        #         # p("MAXSCALEDENOM 9001")
        #         p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
        #         p("LABELITEM", "aantal_woningen")

        #         with block("PROJECTION"):
        #             q("init=epsg:28992")
                
        #         with block("METADATA"):
        #             q("ows_title", layer_name)
        #             q('ows_group_title', group)
        #             q("wms_include_items", "all")
        #             q("ows_abstract", "Servicegebieden locaties")
        #             q("gml_featureid", "id")
        #             q("gml_geometries", "geometry")
        #             q("gml_geometry_type", "point")
        #             q("gml_include_items", "all")
        #             q("gml_types", "auto")
        #             q("wms_enable_request", "!GetLegendGraphic")
                

        #         for i in range(10):

        #             with block("CLASS"):
        #                 p("NAME", f"{i}")

        #                 # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
        #                 # de laatste digit wordt gebruikt om zowel een groep te maken als een kleur uit de lijst te pakken, 
        #                 #dat maakt dat zowel het cluster als het gebied dezelfde kleur krijgen.
        #                 print (f'EXPRESSION ("[last_numeric_digit]" eq "{i}")')
        #                 with block("STYLE"):
        #                     p("SYMBOL", "stip")
        #                     p("SIZE 16")
        #                     p(f"COLOR '{colors[i]}'")
        #                     p('OUTLINECOLOR 0 0 0')
        #                     p ('WIDTH 1')

        #                 with block("LABEL"):
        #                     p("MINSCALEDENOM 100")
        #                     p("MAXSCALEDENOM 1000")
        #                     p("COLOR 0 0 0")
        #                     p("OUTLINECOLOR 255 255 255")
        #                     p("OUTLINEWIDTH 3")
        #                     p("FONT", "Ubuntu-M")
        #                     p("TYPE truetype")
        #                     p("SIZE 10")
        #                     p("POSITION AUTO")
        #                     p("PARTIALS FALSE")
        #                     p("OFFSET -30 10")